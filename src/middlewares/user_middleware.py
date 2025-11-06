from aiogram import BaseMiddleware
from typing import (Callable, Awaitable , Any, Dict)


from src.database.models.user import User


class UserMiddleware(BaseMiddleware):
    async def __call__(
        
        self, handler: Callable[[Dict[str, Any]],Awaitable[Any]],
        event: Dict[str, Any],
        data: Dict[str, Any])-> Any:
        
        telegram_user = event.from_user
        user = await User.find_user_by_telegram_id(telegram_user.id)
        if not user:
            await User.create_user(
                telegram_id= telegram_user.id,
                first_name= telegram_user.first_name,
                last_name= telegram_user.last_name,
                username= telegram_user.username
            )
            user = await User.find_user_by_telegram_id(telegram_user.id)
        data["user"] = user
        return await handler(event, data)