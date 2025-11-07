from aiogram import Router, types, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import os
from pathlib import Path
import tempfile, os
from aiogram.types import FSInputFile

from src.utils.pdf_builder import build_pdf_from_contents
from src.state.pdf_states import PDFStates

router = Router()

def pdf_main_kb():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 افزودن متن", callback_data="pdf_add_text"),InlineKeyboardButton(text="🖼 افزودن عکس", callback_data="pdf_add_image")],
        [InlineKeyboardButton(text="🔠 تنظیم فونت/سایز", callback_data="pdf_set_font")],
        [InlineKeyboardButton(text="🔀 ترتیب صفحات", callback_data="pdf_reorder")],
        [InlineKeyboardButton(text="👀 پیش‌نمایش", callback_data="pdf_preview")],
        [InlineKeyboardButton(text="✅ ساخت PDF", callback_data="pdf_build"),InlineKeyboardButton(text="❌ لغو", callback_data="pdf_cancel")],
    ])
    return kb

@router.callback_query(F.data == "create_pdf")
async def cmd_create_pdf(callback: types.CallbackQuery, state: FSMContext):
    # شروع جلسه ساخت PDF — اطلاعات جلسه رو در FSM ذخیره میکنیم
    await state.set_state(PDFStates.choosing_action)
    # داده‌های اولیه: contents = لیستی از آیتم‌ها با نوع 'text' یا 'image'
    await state.update_data(contents=[])  
    # تنظیمات پیش‌فرض فونت
    await state.update_data(font={"name":"Helvetica","size":12, "align":"left"})
    await callback.message.edit_text("🎛 جلسه ساخت PDF آغاز شد. یکی از گزینه‌ها رو انتخاب کن:", reply_markup=pdf_main_kb())
    
@router.callback_query(F.data == "pdf_add_text")
async def cb_pdf_add_text(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(PDFStates.waiting_for_text)
    await callback.message.edit_text("📝 لطفا متن رو ارسال کن. (برای چند پاراگراف، هر پیام یک صفحه در نظر گرفته میشه)\nیا /cancel برای انصراف")

@router.callback_query(F.data == "pdf_add_image")
async def cb_pdf_add_image(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(PDFStates.waiting_for_image)
    await callback.message.edit_text("🖼 لطفا عکس(ها) رو بفرست. هر عکس یک صفحه خواهد شد.\nیا /cancel برای انصراف")

@router.callback_query(F.data == "pdf_set_font")
async def cb_pdf_set_font(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(PDFStates.waiting_for_font)
    await callback.answer("فلا این قابلیت در دست توسعه است.")
    # await callback.message.edit_text("🔠 فونت و سایز رو اینطوری بفرست: `FontName 14` (مثال: Vazir 14)\nیا /cancel")

@router.message(PDFStates.waiting_for_text)
async def handle_text(message: types.Message, state: FSMContext):
    text = message.text or ""
    data = await state.get_data()
    contents = data.get("contents", [])
    # هر آیتم: {"type":"text","content": "..."}
    contents.append({"type":"text","content": text})
    await state.update_data(contents=contents)
    await message.answer("✅ متن اضافه شد.", reply_markup=pdf_main_kb())
    await state.set_state(PDFStates.choosing_action)
    


TEMP_DIR = Path("tmp/pdf_sessions")
TEMP_DIR.mkdir(parents=True, exist_ok=True)

@router.message(PDFStates.waiting_for_image, F.photo)
async def handle_image(message: types.Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]  # بزرگترین کیفیت
    user_id = message.from_user.id
    session_dir = TEMP_DIR / str(user_id)
    session_dir.mkdir(parents=True, exist_ok=True)
    filename = session_dir / f"{photo.file_unique_id}.jpg"
    await bot.download(photo, destination=filename)  # ذخیره محلی
    data = await state.get_data()
    contents = data.get("contents", [])
    contents.append({"type":"image","path": str(filename)})
    await state.update_data(contents=contents)
    await message.answer("✅ عکس اضافه شد.", reply_markup=pdf_main_kb())
    await state.set_state(PDFStates.choosing_action)

@router.message(PDFStates.waiting_for_font)
async def handle_font(message: types.Message, state: FSMContext):
    text = message.text.strip()
    parts = text.split()
    if len(parts) >= 2 and parts[-1].isdigit():
        size = int(parts[-1])
        font_name = " ".join(parts[:-1])
        await state.update_data(font={"name":font_name,"size":size})
        await message.answer(f"✅ فونت تنظیم شد: {font_name} — {size}pt", reply_markup=pdf_main_kb())
        await state.set_state(PDFStates.choosing_action)
    else:
        await message.answer("فرمت اشتباهه. مثل: `Vazir 14`")
        
@router.callback_query(F.data.startswith("pdf_remove_"))
async def cb_pdf_remove(callback: types.CallbackQuery, state: FSMContext):
    idx = int(callback.data.replace("pdf_remove_",""))
    data = await state.get_data()
    contents = data.get("contents", [])
    if 0 <= idx < len(contents):
        item = contents.pop(idx)
        # اگر فایل عکس بوده، حذف فیزیکی هم بکن
        if item["type"]=="image" and Path(item["path"]).exists():
            Path(item["path"]).unlink(missing_ok=True)
        await state.update_data(contents=contents)
        await callback.answer("✅ حذف شد")
    else:
        await callback.answer("❌ ایندکس نامعتبر", show_alert=True)
    await callback.message.edit_text("بازگشت به منو.", reply_markup=pdf_main_kb())
    await state.set_state(PDFStates.choosing_action)
    

@router.callback_query(F.data == "pdf_cancel")
async def cb_pdf_cancel(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ ساخت PDF لغو شد.")

@router.callback_query(F.data == "pdf_reorder")
async def cb_pdf_reorder(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    contents = data.get("contents", [])
    if not contents:
        return await callback.answer("📄 هنوز محتوایی وجود نداره.", show_alert=True)
    
    text = "🔀 ترتیب فعلی صفحات:\n\n"
    for i, it in enumerate(contents, start=1):
        t = "📝 متن" if it["type"]=="text" else "🖼 عکس"
        text += f"{i}. {t}\n"
    
    await callback.message.edit_text(text, reply_markup=pdf_main_kb())
    
@router.callback_query(F.data == "pdf_build")
async def cb_pdf_build(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    contents = data.get("contents", [])
    font = data.get("font", {"name":"Helvetica","size":12})
    if not contents:
        await callback.answer("هیچ محتوایی وجود نداره!", show_alert=True)
        return

    user_id = callback.from_user.id
    out_file = f"tmp/pdf_sessions/{user_id}/output.pdf"
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)

    await callback.message.edit_text("⏳ در حال ساخت PDF...")
    build_pdf_from_contents(contents, font, out_file)

    await bot.send_document(
    chat_id=user_id,
    document=FSInputFile(out_file),
    caption="فایل PDF شما آماده است ✅"
)
    await callback.message.edit_text("📁 PDF ساخته شد و برای شما ارسال شد.", reply_markup=pdf_main_kb())
    await state.set_state(PDFStates.choosing_action)


