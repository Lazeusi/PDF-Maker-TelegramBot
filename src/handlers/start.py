from aiogram import types, Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

router = Router()

@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    await message.reply("برای ساخت PDF از منوی پایین استفاده کنید.", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="ساخت PDF 📝", callback_data="create_pdf")],
    ]))