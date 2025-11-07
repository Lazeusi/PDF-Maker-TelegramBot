import os
import logging
import re
from bidi.algorithm import get_display
import arabic_reshaper
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ثبت فونت فارسی
FONT_PATH = "src/assets/fonts/Vazir.ttf"
if os.path.exists(FONT_PATH):
    pdfmetrics.registerFont(TTFont("Vazir", FONT_PATH))
else:
    logging.warning("⚠️ فونت Vazir یافت نشد، از Helvetica استفاده می‌شود.")

def is_persian(text: str) -> bool:
    """بررسی اینکه متن فارسی هست یا نه"""
    return bool(re.search(r'[\u0600-\u06FF]', text))

def build_pdf_from_contents(contents: list, font: dict, output_file: str):
    logging.info(f"📦 CONTENTS: {contents}")

    doc = SimpleDocTemplate(output_file, pagesize=A4)
    story = []

    font_name = "Vazir" if "Vazir" in pdfmetrics.getRegisteredFontNames() else "Helvetica"
    font_size = font.get("size", 14)

    style_rtl = ParagraphStyle(
        name="RTLText",
        fontName=font_name,
        fontSize=font_size,
        leading=font_size + 4,
        alignment=2,  # راست‌چین
    )

    style_ltr = ParagraphStyle(
        name="LTRText",
        fontName=font_name,
        fontSize=font_size,
        leading=font_size + 4,
        alignment=0,  # چپ‌چین
    )

    for content in contents:
        if content["type"] == "text":
            text = content.get("content", "").strip()
            if not text:
                continue

            # تشخیص فارسی یا انگلیسی
            if is_persian(text):
                reshaped = arabic_reshaper.reshape(text)
                bidi_text = get_display(reshaped)
                story.append(Paragraph(bidi_text, style_rtl))
            else:
                story.append(Paragraph(text, style_ltr))

            story.append(Spacer(1, 0.2 * inch))

        elif content["type"] == "image":
            path = content.get("path")
            if not path or not os.path.exists(path):
                logging.warning(f"⚠️ تصویر پیدا نشد: {path}")
                continue

            img = Image(path)
            max_width, max_height = 500, 700
            if img.drawWidth > max_width or img.drawHeight > max_height:
                ratio = min(max_width / img.drawWidth, max_height / img.drawHeight)
                img.drawWidth *= ratio
                img.drawHeight *= ratio

            story.append(img)
            story.append(Spacer(1, 0.3 * inch))

    doc.build(story)
    logging.info(f"✅ PDF ساخته شد: {output_file}")
