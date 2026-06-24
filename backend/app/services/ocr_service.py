import easyocr

# Lazy singleton — avoids loading the model at import time (slow, blocks startup)
_reader = None


def _get_reader():
    global _reader
    if _reader is None:
        _reader = easyocr.Reader(['en'])
    return _reader


def extract_text_from_image(image_path):
    reader = _get_reader()
    results = reader.readtext(image_path)

    text = ""
    for result in results:
        text += result[1] + "\n"

    return text