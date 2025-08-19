import fitz  # PyMuPDF
import os


def render_pdf_page_to_image(pdf_path, page_number):

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return None

    try:

        doc = fitz.open(pdf_path)

        if 0 <= page_number < doc.page_count:
            page = doc.load_page(page_number)

            pix = page.get_pixmap(dpi=200)

            img_data = pix.tobytes("png")
            doc.close()
            return img_data
        else:
            print(f"Error: Invalid page number {page_number} for PDF with {doc.page_count} pages.")
            doc.close()
            return None
    except Exception as e:
        print(f"An error occurred while rendering PDF page: {e}")
        return None

