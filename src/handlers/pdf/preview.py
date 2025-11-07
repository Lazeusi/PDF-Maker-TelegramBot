from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from src.state.pdf_states import PDFStates

from .create import pdf_main_kb

router = Router()

@router.callback_query(F.data == "pdf_preview")
async def cb_pdf_preview(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    contents = data.get("contents", [])
    if not contents:
        return await callback.message.edit_text("هیچ محتوایی اضافه نشده.", reply_markup=pdf_main_kb())

    text = "📄 محتویات فعلی:\n\n"
    for i, it in enumerate(contents, start=1):
        t = "متن" if it["type"]=="text" else "عکس"
        preview = (it["content"][:50] + "...") if it["type"]=="text" else it["path"].split("/")[-1]
        text += f"{i}. [{t}] {preview}\n"

    # دکمه حذف هر صفحه و بازگشت
    kb = InlineKeyboardMarkup(inline_keyboard=[
        *[[InlineKeyboardButton(text=f"حذف {i+1}", callback_data=f"pdf_remove_{i}")] for i in range(len(contents))],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="pdf_back_to_menu")]
    ])
    await callback.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "pdf_back_to_menu")
async def cb_pdf_back_to_menu(callback: types.CallbackQuery):
    await callback.message.edit_text("🎛 جلسه ساخت PDF ادامه دارد. یکی از گزینه‌ها رو انتخاب کن:", reply_markup=pdf_main_kb())