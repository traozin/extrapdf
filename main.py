import fitz
from PIL import Image
import os
import pytesseract

tesseract_path = os.path.join(os.path.dirname(__file__), "tesseract", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

tessdata_dir = os.path.join(os.path.dirname(__file__), "tesseract", "tessdata")
os.environ["TESSDATA_PREFIX"] = tessdata_dir

def extract_text_from_pdf_with_ocr(pdf_path, output_dir):
    pdf_document = fitz.open(pdf_path)
    all_text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        all_text += f"\n\n--- Página {page_num + 1} ---\n\n"

        pix = page.get_pixmap(dpi=75)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        text = pytesseract.image_to_string(img, lang="por")
        all_text += text + "\n"

    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(pdf_path))[0] + ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_text)

    pdf_document.close()
