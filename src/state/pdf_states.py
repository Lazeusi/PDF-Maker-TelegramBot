from aiogram.fsm.state import State, StatesGroup

class PDFStates(StatesGroup):
    choosing_action = State()       # منوی اصلی داخل جلسه‌ی ساخت PDF
    waiting_for_text = State()      # کاربر داره متن میفرسته
    waiting_for_image = State()     # کاربر داره عکس میفرسته
    waiting_for_font = State()      # کاربر داره فونت/سایز انتخاب میکنه
    waiting_for_reorder = State()   # کاربر داره ترتیب صفحات رو میده
    confirming = State()            # تایید نهایی و ساخت
