from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from config.tariffs import TARIFFS
from keyboards import kb_experience, kb_capital, kb_confirm, kb_back_to_start
from utils.states import SurveyStates
from utils.validators import validate_name, validate_username, sanitize_text
from services import sheets_service, notify_admins, crm_service

router = Router(name="survey")


# ──────────────────────────────────────────────────────────────────────────────
# ШАГ 1: Выбор тарифа
# ──────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("tariff:"), SurveyStates.choosing_tariff)
async def tariff_selected(callback: CallbackQuery, state: FSMContext) -> None:
    tariff_id = callback.data.split(":")[1]
    tariff = TARIFFS.get(tariff_id)

    if not tariff:
        await callback.answer("❌ Тариф не найден", show_alert=True)
        return

    await state.update_data(
        tariff_id=tariff.id,
        tariff_name=tariff.name,
        tariff_price=tariff.price_label,
    )
    await state.set_state(SurveyStates.entering_name)

    await callback.message.edit_text(
        text=(
            f"✅ Отличный выбор! Ты выбрал тариф <b>{tariff.name} — {tariff.price_label}</b>\n\n"
            "👤 Как тебя зовут? Введи своё имя:"
        ),
        parse_mode="HTML",
    )
    await callback.answer()


# ──────────────────────────────────────────────────────────────────────────────
# ШАГ 2: Имя
# ──────────────────────────────────────────────────────────────────────────────

@router.message(SurveyStates.entering_name)
async def name_entered(message: Message, state: FSMContext) -> None:
    is_valid, error = validate_name(message.text or "")
    if not is_valid:
        await message.answer(f"{error}\n\nВведи своё имя ещё раз:")
        return

    clean_name = sanitize_text(message.text.strip())
    await state.update_data(name=clean_name)
    await state.set_state(SurveyStates.choosing_experience)

    await message.answer(
        text=(
            f"Приятно познакомиться, <b>{clean_name}</b>! 👋\n\n"
            "💼 У тебя есть опыт в P2P-трейдинге?"
        ),
        reply_markup=kb_experience(),
        parse_mode="HTML",
    )


# ──────────────────────────────────────────────────────────────────────────────
# ШАГ 3: Опыт
# ──────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("exp:"), SurveyStates.choosing_experience)
async def experience_selected(callback: CallbackQuery, state: FSMContext) -> None:
    exp_value = callback.data.split(":")[1]  # "yes" или "no"
    exp_label = "✅ Да, есть опыт" if exp_value == "yes" else "❌ Нет, новичок"

    await state.update_data(experience=exp_value, experience_label=exp_label)
    await state.set_state(SurveyStates.choosing_capital)

    await callback.message.edit_text(
        text=(
            f"Записал: <b>{exp_label}</b>\n\n"
            "💰 Каков твой начальный капитал для P2P?"
        ),
        reply_markup=kb_capital(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_experience", SurveyStates.choosing_capital)
async def back_to_experience(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(SurveyStates.choosing_experience)
    await callback.message.edit_text(
        text="💼 У тебя есть опыт в P2P-трейдинге?",
        reply_markup=kb_experience(),
        parse_mode="HTML",
    )
    await callback.answer()


# ──────────────────────────────────────────────────────────────────────────────
# ШАГ 4: Капитал
# ──────────────────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("capital:"), SurveyStates.choosing_capital)
async def capital_selected(callback: CallbackQuery, state: FSMContext) -> None:
    capital = callback.data.split(":", 1)[1]
    await state.update_data(capital=capital)

    # Получаем Telegram username
    username = callback.from_user.username
    if username:
        # Username доступен — сохраняем сразу
        await state.update_data(
            username=f"@{username}",
            telegram_id=callback.from_user.id,
        )
        await _show_confirmation(callback.message, state)
    else:
        # Username скрыт — просим ввести вручную
        await state.set_state(SurveyStates.entering_username)
        await state.update_data(telegram_id=callback.from_user.id)
        await callback.message.edit_text(
            text=(
                "📱 У тебя не установлен username в Telegram.\n\n"
                "Пожалуйста, введи свой username вручную\n"
                "(или напиши любое имя для связи):"
            ),
        )

    await callback.answer()


# ──────────────────────────────────────────────────────────────────────────────
# ШАГ 5 (опциональный): Ввод username вручную
# ──────────────────────────────────────────────────────────────────────────────

@router.message(SurveyStates.entering_username)
async def username_entered(message: Message, state: FSMContext) -> None:
    text = (message.text or "").strip()

    # Пробуем как username
    is_valid, result = validate_username(text)
    if is_valid:
        await state.update_data(username=result)
    else:
        # Принимаем как свободный текст (например, ник или имя)
        await state.update_data(username=sanitize_text(text))

    await _show_confirmation(message, state)


# ──────────────────────────────────────────────────────────────────────────────
# ШАГ 6: Подтверждение
# ──────────────────────────────────────────────────────────────────────────────

async def _show_confirmation(event, state: FSMContext) -> None:
    """Показать сводку данных для подтверждения."""
    data = await state.get_data()
    await state.set_state(SurveyStates.confirming)

    exp_label = "✅ Есть опыт" if data.get("experience") == "yes" else "❌ Новичок"

    text = (
        "📋 <b>Проверь свои данные:</b>\n\n"
        f"📦 Тариф: <b>{data['tariff_name']} — {data['tariff_price']}</b>\n"
        f"👤 Имя: <b>{data['name']}</b>\n"
        f"📱 Username: <b>{data['username']}</b>\n"
        f"💼 Опыт: <b>{exp_label}</b>\n"
        f"💰 Капитал: <b>{data['capital']}</b>\n\n"
        "Всё верно?"
    )

    send_fn = event.edit_text if hasattr(event, "edit_text") else event.answer
    await send_fn(text=text, reply_markup=kb_confirm(), parse_mode="HTML")


@router.callback_query(F.data == "confirm:edit", SurveyStates.confirming)
async def confirm_edit(callback: CallbackQuery, state: FSMContext) -> None:
    """Сброс и начало заново."""
    data = await state.get_data()
    await state.clear()
    # Возвращаем только тариф, остальное переспрашиваем
    await callback.message.edit_text(
        text="🔄 Хорошо, давай начнём сначала.\n\nНажми /start чтобы начать снова.",
        reply_markup=kb_back_to_start(),
    )
    await callback.answer()


@router.callback_query(F.data == "confirm:yes", SurveyStates.confirming)
async def confirm_yes(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    """Финальное подтверждение — сохраняем и уведомляем."""
    data = await state.get_data()
    await state.clear()

    tariff_name = data.get("tariff_name", "")
    tariff_price = data.get("tariff_price", "")

    # Уведомляем пользователя немедленно
    await callback.message.edit_text(
        text=(
            f"🎉 <b>Заявка принята!</b>\n\n"
            f"Ты выбрал тариф <b>{tariff_name} — {tariff_price}</b>.\n\n"
            "В ближайшее время с тобой свяжутся для оплаты и доступа к обучению.\n\n"
            "📲 Ожидай сообщения от нашего менеджера!\n\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            "Если возникнут вопросы — просто напиши /start"
        ),
        parse_mode="HTML",
    )
    await callback.answer("✅ Заявка отправлена!")

    # Сохраняем в Google Sheets (не блокируем ответ пользователю)
    sheets_ok = await sheets_service.save_application(data)
    if not sheets_ok:
        logger.error(f"Не удалось сохранить заявку в Sheets: {data}")

    # Отправляем в CRM (если настроена)
    await crm_service.create_lead(data)

    # Уведомляем администраторов
    await notify_admins(bot, data)

    logger.info(
        f"Новая заявка оформлена: "
        f"user={data.get('telegram_id')} "
        f"tariff={tariff_name} "
        f"sheets={'ok' if sheets_ok else 'FAIL'}"
    )

