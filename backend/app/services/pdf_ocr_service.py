from pdf2image import convert_from_path
from app.services.ocr_service import extract_text_from_image
from app.config.config import POPPLER_PATH
import logging
import os

logger = logging.getLogger(__name__)


def extract_text_with_ocr(pdf_path):

    kwargs = {}
    if POPPLER_PATH:
        kwargs["poppler_path"] = POPPLER_PATH

    images = convert_from_path(pdf_path, **kwargs)

    full_text = ""

    for i, image in enumerate(images):

        image_path = f"temp_page_{i}.png"

        image.save(image_path)

        full_text += extract_text_from_image(
            image_path
        )

        os.remove(image_path)

    logger.debug("OCR extracted %d chars", len(full_text))

    return full_text