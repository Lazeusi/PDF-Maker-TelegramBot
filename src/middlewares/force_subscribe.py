from aiogram import BaseMiddleware, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Callable, Dict, Any, Awaitable, Union
from src.database.models.channel import Channel


class ForceSubscribeMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:

        if isinstance(event, Message):
            user_id = event.from_user.id
            channels = await Channel.get_all_channels()

            if not channels:
                return await handler(event, data)

            not_joined = []

            for ch in channels:
                try:
                    member = await self.bot.get_chat_member(ch["chat_id"], user_id)
                    if member.status in ("left", "kicked"):
                        not_joined.append(ch)
                except Exception:
                    continue

            if not_joined:
                buttons = []
                for ch in not_joined:
                    try:
                        invite_link = await self.bot.export_chat_invite_link(ch["chat_id"])
                    except Exception:
                        invite_link = None

                    buttons.append([
                        InlineKeyboardButton(
                            text=f"📢 عضویت در {ch['title']}",
                            url=invite_link
                        )
                    ])

                buttons.append([
                    InlineKeyboardButton(text="✅ عضو شدم", callback_data="check_subscription")
                ])

                markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                await event.answer(
                    "👋 برای استفاده از ربات باید در کانال‌های زیر عضو بشی:",
                    reply_markup=markup
                )
                return  

        return await handler(event, data)
