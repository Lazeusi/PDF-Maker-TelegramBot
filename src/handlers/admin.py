from aiogram import types, F , Router, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from src.database.models.admin import Admin
from src.database.models.user import User
from src.database.models.channel import Channel
from src.keyboards.admin import (admin_keyboard, force_join_keyboard,
                                 check_channel_type_keyboard,
                                 channel_list , channel_list_show,
                                 back_to_channel_menu_keyboard,
                                 admin_panel_keyboard,admin_list_remove,
                                 )
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
    await message.answer("✅ شما به عنوان مالک ربات فعال شدید.")
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
        
@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    is_owner = await Admin.find_admin_by_telegram_id(callback.from_user.id)
    if is_owner.is_owner == True:
        await callback.message.edit_text("پنل ادمین:", reply_markup=admin_panel_keyboard)
    else:
        await callback.answer("فقط مالک ربات به این پنل دسترسی دارد.", show_alert=True)

class AddAdminState(StatesGroup):
    waiting_for_telegram_id = State()
@router.callback_query(F.data == "add_admin")
async def add_admin_callback(callback: types.CallbackQuery , state: FSMContext):
    await callback.message.edit_text("لطفا آیدی تلگرام کاربر را ارسال کنید تا به عنوان ادمین اضافه شود.")
    await state.set_state(AddAdminState.waiting_for_telegram_id)
    
@router.message(AddAdminState.waiting_for_telegram_id)
async def handle_add_admin(message: types.Message, state: FSMContext):
    id = message.text.strip()
    if not id.isdigit():
        user = await User.find_user_by_username(message.text.strip().lstrip("@"))
        if not user:
            return await message.answer("کاربر با این آیدی یا یوزرنیم پیدا نشد. لطفا دوباره امتحان کنید.")
        await Admin.create_admin(
            telegram_id= user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_owner=False
        )
        await message.answer(f"✅ کاربر @{user.username} به عنوان ادمین اضافه شد.")
        await state.clear()
    elif id.isdigit():
        telegram_id = int(id)
        user = await User.find_user_by_telegram_id(telegram_id)
        if not user:
            return await message.answer("کاربر با این آیدی یا یوزرنیم پیدا نشد. لطفا دوباره امتحان کنید.")
        await Admin.create_admin(
            telegram_id= user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            is_owner=False
        )
        await message.answer(f"✅ کاربر @{user.username} به عنوان ادمین اضافه شد.")
        await state.clear()
    else:
        return await message.answer("کاربر با این آیدی یا یوزرنیم پیدا نشد. لطفا دوباره امتحان کنید.")
    
@router.callback_query(F.data == "remove_admin")
async def remove_admin_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("لطفا ادمینی که میخواهید حذف کنید را انتخاب کنید" , reply_markup=await admin_list_remove())
        
@router.callback_query(F.data.startswith("remove_admin_"))
async def confirm_remove_admin_callback(callback: types.CallbackQuery):
    telegram_id = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        f"آیا از حذف این ادمین مطمئن هستید؟\nTelegram ID: `{telegram_id}`",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="✅ بله", callback_data=f"confirm_remove_admin_{telegram_id}"),
                types.InlineKeyboardButton(text="❌ خیر", callback_data="back_to_admin_panel")
            ]
        ]))
@router.callback_query(F.data.startswith("confirm_remove_admin_"))
async def perform_remove_admin_callback(callback: types.CallbackQuery):
    telegram_id = int(callback.data.split("_")[3])
    await Admin.collection.delete_one({"telegram_id": telegram_id})
    await callback.message.edit_text("✅ ادمین با موفقیت حذف شد!")
    
    
@router.callback_query(F.data == "list_admins")
async def list_admins_callback(callback: types.CallbackQuery):
    admins = await Admin.get_all_admins()
    if not admins:
        return await callback.message.edit_text("هیچ ادمینی وجود ندارد.", reply_markup=back_to_channel_menu_keyboard)
    
    text = "<b>لیست ادمین‌ها:</b>\n\n"
    for admin in admins:
        display_name = f"@{admin.username}" if admin.username else str(admin.telegram_id)
        text += f"- {display_name} (ID: <code>{admin.telegram_id}</code>)\n"
    
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to_channel_menu_keyboard)