import os
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# Configuração do pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

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

def process_pdfs_in_directory_with_ocr(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file_name in os.listdir(input_dir):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, file_name)
            print(f"Processando com OCR: {file_name}")
            extract_text_from_pdf_with_ocr(pdf_path, output_dir)

if __name__ == "__main__":
    input_directory = "./pdfs"  # Diretório de entrada
    output_directory = "./output"  # Diretório de saída

    process_pdfs_in_directory_with_ocr(input_directory, output_directory)
    print("Processamento com OCR concluído!")