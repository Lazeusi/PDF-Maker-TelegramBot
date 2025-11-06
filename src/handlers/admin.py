from aiogram import types, F , Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.models.admin import Admin
from src.database.models.channel import Channel
from src.keyboards.admin import (admin_keyboard, force_join_keyboard,
                                 check_channel_type_keyboard,
                                 channel_list , channel_list_show,
                                 back_to_channel_menu_keyboard)
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
    
@router.callback_query(F.data == "remove_channel")
async def remove_channel_handler(callback: types.CallbackQuery):
    await callback.message.edit_text("لطفا چنلی که میخواهید حذف کنید را انتخاب کنید" , reply_markup=await channel_list())
    
class DeleteChannelState(StatesGroup):
    waiting_for_accept = State()
    
@router.callback_query(F.data.startswith("channel_"))
async def delete_channel_callback(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[1])
    await callback.message.edit_text(
        f"آیا از حذف این کانال مطمئن هستید؟\nChat ID: `{chat_id}`",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ بله", callback_data=f"confirm_delete_{chat_id}"),
                types.InlineKeyboardButton(text="❌ خیر", callback_data="back_to_channel_menu")
            ]
        ])
    )
@router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete_channel_callback(callback: types.CallbackQuery):
    chat_id = int(callback.data.split("_")[2])
    result = await Channel.collection.delete_one({"chat_id": chat_id})
    if result.deleted_count:
        await callback.message.edit_text("✅ کانال با موفقیت حذف شد!")
        
@router.callback_query(F.data == "list_channels")
async def list_channels_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("لیست کانال‌ها:", reply_markup=await channel_list_show())
    
@router.callback_query(F.data.startswith("show_channel_"))
async def show_channel_callback(callback: types.CallbackQuery):
    chat_id_str = callback.data.replace("show_channel_", "")
    try:
        chat_id = int(chat_id_str)
    except ValueError:
        return await callback.answer("❌ chat_id نامعتبره", show_alert=True)

    channel = await Channel.collection.find_one({"chat_id": chat_id})
    if channel:
        await callback.message.edit_text(
    f"<b>📡 اطلاعات کانال:</b>\n\n"
    f"<b>Title:</b> {channel['title']}\n"
    f"<b>Username:</b> @{channel['username'] if channel.get('username') else 'N/A'}\n"
    f"<b>Chat ID:</b> <code>{channel['chat_id']}</code>\n"
    f"<b>Type:</b> {channel['type'].capitalize()}",
    parse_mode="HTML",
    reply_markup=back_to_channel_menu_keyboard
)
    else:
        await callback.answer("❌ کانال پیدا نشد!", show_alert=True)