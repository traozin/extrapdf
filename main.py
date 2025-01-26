import fitz  # PyMuPDF
from PIL import Image
import os
import pytesseract

# Caminho relativo ao executável do Tesseract no projeto
tesseract_path = os.path.join(os.path.dirname(__file__), "tesseract", "tesseract.exe")
pytesseract.pytesseract.tesseract_cmd = tesseract_path

# Define o caminho do diretório "tessdata" onde estão os arquivos .traineddata
tessdata_dir = os.path.join(os.path.dirname(__file__), "tesseract", "tessdata")
os.environ["TESSDATA_PREFIX"] = tessdata_dir  # Configura a variável de ambiente

def extract_text_from_pdf_with_ocr(pdf_path, output_dir):
    # Carrega o PDF
    pdf_document = fitz.open(pdf_path)
    all_text = ""

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        all_text += f"\n\n--- Página {page_num + 1} ---\n\n"

        # Extrai a página como imagem
        pix = page.get_pixmap(dpi=300)  # Ajusta a resolução para melhorar o OCR
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Executa o OCR na imagem da página
        text = pytesseract.image_to_string(img, lang="por")
        all_text += text + "\n"

    # Salva o texto extraído no arquivo de saída
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(pdf_path))[0] + ".txt")
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_text)

    pdf_document.close()
