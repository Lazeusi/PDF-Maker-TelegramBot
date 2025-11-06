from aiogram import Router, F, types

from src.keyboards.admin import admin_keyboard , force_join_keyboard

router = Router()

@router.callback_query(F.data == "back_to_admin_panel")
async def admin_panel_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("شما به منوی اصلی بازگشتید", reply_markup=admin_keyboard)
    
@router.callback_query(F.data == "back_to_channel_menu")
async def back_to_channel_menu_callback(callback: types.CallbackQuery):
    await callback.message.edit_text("لطفا انتخاب کنید:", reply_markup=force_join_keyboard)