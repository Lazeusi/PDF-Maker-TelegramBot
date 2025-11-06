from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery

router = Router()

@router.callback_query(F.data == "check_subscription")
async def recheck_subscription(callback: CallbackQuery, bot: Bot):
    from src.database.models.channel import Channel

    channels = await Channel.get_all_channels()
    not_joined = []

    for ch in channels:
        try:
            member = await bot.get_chat_member(ch["chat_id"], callback.from_user.id)
            if member.status in ("left", "kicked"):
                not_joined.append(ch)
        except Exception:
            continue

    if not_joined:
        await callback.answer("❌ هنوز عضو همه‌ی کانال‌ها نشدی!", show_alert=True)
    else:
        await callback.message.delete()
        await callback.message.answer("✅ عالی! حالا می‌تونی از ربات استفاده کنی 😎")
