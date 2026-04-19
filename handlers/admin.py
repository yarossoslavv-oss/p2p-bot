from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from loguru import logger

from config.settings import ADMIN_IDS
from services import sheets_service

router = Router(name="admin")


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    """Панель администратора."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У тебя нет доступа к этой команде.")
        return

    text = (
        "🛠 <b>Панель администратора</b>\n\n"
        "Доступные команды:\n"
        "/stats — статистика заявок\n"
        "/healthcheck — проверка подключений\n"
        "/broadcast — (в разработке) рассылка\n"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("healthcheck"))
async def cmd_healthcheck(message: Message) -> None:
    """Проверить подключения к внешним сервисам."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа.")
        return

    await message.answer("⏳ Проверяю подключения...")

    sheets_ok = sheets_service.health_check()

    status_sheets = "✅ Google Sheets" if sheets_ok else "❌ Google Sheets — ошибка подключения"

    text = (
        "🔍 <b>Health Check</b>\n\n"
        f"{status_sheets}\n"
        "✅ Telegram Bot API\n"
    )
    await message.answer(text, parse_mode="HTML")
    logger.info(f"Health check от админа {message.from_user.id}: sheets={sheets_ok}")


@router.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    """Базовая статистика (заглушка — подключи реальные данные из Sheets)."""
    if not is_admin(message.from_user.id):
        await message.answer("❌ Нет доступа.")
        return

    # TODO: подключить реальный подсчёт строк из Google Sheets
    text = (
        "📊 <b>Статистика</b>\n\n"
        "Для просмотра заявок открой Google Sheets.\n\n"
        "🔗 Расширение: можно подключить подсчёт строк через gspread."
    )
    await message.answer(text, parse_mode="HTML")

