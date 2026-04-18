"""
P2P Trading Bot — точка входа.
Запуск: python bot.py
"""

import asyncio
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import BOT_TOKEN, LOG_LEVEL, ADMIN_IDS
from handlers import start_router, survey_router, admin_router
from middlewares import LoggingMiddleware


# ── Логирование ───────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan> — {message}",
)
logger.add(
    "logs/bot.log",
    level="DEBUG",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    encoding="utf-8",
)


async def on_startup(bot: Bot) -> None:
    me = await bot.get_me()
    logger.info(f"Бот запущен: @{me.username} (id={me.id})")

    # Уведомить всех админов о старте
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "✅ <b>Бот запущен!</b>", parse_mode="HTML")
        except Exception:
            pass


async def on_shutdown(bot: Bot) -> None:
    logger.warning("Бот останавливается...")
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "⛔ <b>Бот остановлен.</b>", parse_mode="HTML")
        except Exception:
            pass


async def main() -> None:
    # Создаём папку для логов если нет
    import os
    os.makedirs("logs", exist_ok=True)

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # FSM Storage — замени на RedisStorage для продакшена
    # from aiogram.fsm.storage.redis import RedisStorage
    # storage = RedisStorage.from_url("redis://localhost:6379")
    storage = MemoryStorage()

    dp = Dispatcher(storage=storage)

    # ── Middlewares ────────────────────────────────────────────────────────────
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    # ── Роутеры (порядок важен!) ───────────────────────────────────────────────
    dp.include_router(admin_router)   # сначала — чтобы /admin не попал в survey
    dp.include_router(start_router)
    dp.include_router(survey_router)

    # ── Lifecycle хуки ────────────────────────────────────────────────────────
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logger.info("Запускаю polling...")
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную (Ctrl+C)")
