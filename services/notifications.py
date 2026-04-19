"""
Сервис уведомлений администратора.
"""

from aiogram import Bot
from loguru import logger

from config.settings import ADMIN_IDS


async def notify_admins(bot: Bot, data: dict) -> None:
    """
    Отправить уведомление всем администраторам о новой заявке.

    data = {
        "name": str,
        "username": str,
        "telegram_id": int,
        "tariff_name": str,
        "tariff_price": str,
        "experience": str,
        "capital": str,
    }
    """
    exp_label = "✅ Есть опыт" if data.get("experience") == "yes" else "❌ Новичок"
    username_display = data.get("username", "не указан")

    text = (
        "🔔 <b>Новая заявка!</b>\n\n"
        f"📦 <b>Тариф:</b> {data.get('tariff_name')} — {data.get('tariff_price')}\n"
        f"👤 <b>Имя:</b> {data.get('name')}\n"
        f"📱 <b>Username:</b> {username_display}\n"
        f"🆔 <b>Telegram ID:</b> <code>{data.get('telegram_id')}</code>\n"
        f"💼 <b>Опыт в P2P:</b> {exp_label}\n"
        f"💰 <b>Капитал:</b> {data.get('capital')}\n\n"
        f"👉 <a href='tg://user?id={data.get('telegram_id')}'>Написать пользователю</a>"
    )

    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id,
                text=text,
                parse_mode="HTML",
            )
            logger.info(f"Уведомление отправлено админу {admin_id}")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление админу {admin_id}: {e}")


async def notify_admin_error(bot: Bot, error: str) -> None:
    """Уведомить администратора об ошибке системы."""
    text = f"⚠️ <b>Системная ошибка</b>\n\n<code>{error}</code>"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, parse_mode="HTML")
        except Exception:
            pass
