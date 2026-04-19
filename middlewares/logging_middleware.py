from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger


class LoggingMiddleware(BaseMiddleware):
    """Логирует все входящие апдейты."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = None

        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"MSG | user={user.id} (@{user.username}) | text={event.text!r}"
            )
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"CBQ | user={user.id} (@{user.username}) | data={event.data!r}"
            )

        try:
            result = await handler(event, data)
            return result
        except Exception as e:
            uid = user.id if user else "unknown"
            logger.exception(f"Необработанная ошибка у пользователя {uid}: {e}")
            raise

