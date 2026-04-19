from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from loguru import logger

from keyboards import kb_start, kb_tariffs, kb_back_to_start
from config.tariffs import TARIFFS
from utils.states import SurveyStates

router = Router(name="start")

WELCOME_TEXT = (
    "👋 <b>Привет! Я бот для обучения P2P-трейдингу.</b>\n\n"
    "💡 <b>Что ты получишь:</b>\n"
    "  📈 Систему заработка на P2P без рисков\n"
    "  🔐 Проверенные схемы арбитража\n"
    "  📊 Готовые стратегии под любой бюджет\n"
    "  🤝 Живое сообщество трейдеров\n\n"
    "👇 Выбери тариф и начни обучение уже сегодня:"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start."""
    await state.clear()
    await message.answer(
        text=WELCOME_TEXT,
        reply_markup=kb_start(),
        parse_mode="HTML",
    )
    logger.info(f"Пользователь {message.from_user.id} запустил бота")


@router.callback_query(F.data == "show_tariffs")
@router.callback_query(F.data == "back_to_tariffs")
async def show_tariffs(callback: CallbackQuery, state: FSMContext) -> None:
    """Показать список тарифов."""
    # Собираем описания всех тарифов
    tariff_descriptions = "\n\n".join(t.full_description for t in TARIFFS.values())
    text = (
        "📦 <b>Выбери тариф обучения:</b>\n\n"
        f"{tariff_descriptions}\n\n"
        "👇 Нажми на тариф, чтобы продолжить:"
    )

    await state.set_state(SurveyStates.choosing_tariff)
    await callback.message.edit_text(
        text=text,
        reply_markup=kb_tariffs(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext) -> None:
    """Вернуться на стартовый экран."""
    await state.clear()
    await callback.message.edit_text(
        text=WELCOME_TEXT,
        reply_markup=kb_start(),
        parse_mode="HTML",
    )
    await callback.answer()

