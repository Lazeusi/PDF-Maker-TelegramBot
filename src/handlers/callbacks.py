from aiogram import Router, F, types

from src.keyboards.admin import admin_keyboard

router = Router()

@router.callback_query(F.data == "back_to_admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("شما به منوی اصلی بازگشتید", reply_markup=admin_keyboard)