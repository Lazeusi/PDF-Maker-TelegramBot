from aiogram import types, Router
from aiogram.filters import CommandStart

router = Router()

@router.message(CommandStart())
async def start_command_handler(message: types.Message):
    await message.reply("Hello! Welcome to the PDF Maker Bot. Send me a document and I'll help you create a PDF!")

