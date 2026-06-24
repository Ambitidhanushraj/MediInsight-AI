import fitz

def extract_text_from_pdf(pdf_path: str):

    text = ""

    doc = fitz.open(pdf_path)

    for page_num, page in enumerate(doc):
        page_text = page.get_text()

        print(f"Page {page_num + 1}: {len(page_text)} characters")

        text += page_text

    doc.close()

    return text