from aiogram import types, F , Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.models.admin import Admin
from src.database.models.channel import Channel
from src.keyboards.admin import (admin_keyboard, force_join_keyboard,
                                 check_channel_type_keyboard)
from src.logger import log


router = Router()

@router.message(Command("active_owner"))
async def active_owner(message: types.Message):
    admin_exists = await Admin.get_all_admins()
    if admin_exists:
        return

    await Admin.create_admin(
        telegram_id= message.from_user.id,
        first_name= message.from_user.first_name,
        last_name= message.from_user.last_name,
        username= message.from_user.username,
        is_owner= True
    )
    log.info(f"""
    \n             -------Owner activated!-------            \n
    -   telegram_id: {message.from_user.id}\n
    -   first_name: {message.from_user.first_name}\n
    -   last_name: {message.from_user.last_name}\n
    -   username: {message.from_user.username}\n
         \n             ------------------------------             \n
                 """)
    
@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    exist = await Admin.find_admin_by_telegram_id(message.from_user.id)
    if not exist:
        return await message.reply("⛔ شما دسترسی ندارید.")
    await message.answer("👋 سلام ادمین!", reply_markup=admin_keyboard)
    
@router.callback_query(F.data == "force_join")
async def force_join_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(f"لطفا انتخاب کنید:", reply_markup=force_join_keyboard)

class AddChannelState(StatesGroup):
    waiting_for_public = State()
    waiting_for_private = State()
    
@router.callback_query(F.data == "add_channel")
async def add_channel_callback(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "لطفا نوع کانال را انتخاب کنید:", 
        reply_markup=check_channel_type_keyboard
        
    )
    
@router.callback_query(F.data.in_(["channel_type_public", "channel_type_private"]))
async def choose_type(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "channel_type_public":
        await state.set_state(AddChannelState.waiting_for_public)
        await callback.message.edit_text("یوزرنیم کانال رو بفرست (مثلاً: `@channel`)")
    else:
        await state.set_state(AddChannelState.waiting_for_private)
        await callback.message.edit_text("یه پیام از کانال پرایوت فوروارد کن 📩")


@router.message(AddChannelState.waiting_for_public)
async def handle_public_channel(message: types.Message, state: FSMContext, bot: Bot):
    text = message.text.strip()

 
    if text.startswith("https://t.me/"):
        text = text.replace("https://t.me/", "")
        if not text.startswith("@"):
            text = "@" + text

    elif not text.startswith("@"):
        text = "@" + text

    try:
        chat = await bot.get_chat(text)

        await Channel.add_channel(
            chat_id=chat.id,
            title=chat.title,
            username=chat.username,
            type="public"
        )

        await message.answer(
            f"✅ کانال `{chat.title}` ثبت شد!\n📡 Chat ID: `{chat.id}`",
            parse_mode="Markdown"
        )

    except Exception as e:
        await message.answer(f"❌ خطا در گرفتن اطلاعات کانال:\n`{e}`", parse_mode="Markdown")

    await state.clear()
    
@router.message(AddChannelState.waiting_for_private, F.forward_from_chat)
async def handle_private_channel(message: types.Message, state: FSMContext):
    chat = message.forward_from_chat
    await Channel.add_channel(chat_id=chat.id, title=chat.title, username=chat.username, type="private")
    await message.answer(f"✅ کانال {chat.title} اضافه شد!")
    await state.clear()