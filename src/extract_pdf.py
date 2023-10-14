import pytesseract
from pathlib import Path
from pdf2image import convert_from_path

root = Path(__file__).parent

def tesseract():
    """Convert PDF to image and extract text

    Preserve some whitespace for parsing reasons
    """
    filepath = Path.joinpath(root, "files", "2023-10-13-11-00-05_Arrest_Log.pdf")
    custom_oem_psm_config = r'--oem 3 --psm 6 -l eng -c preserve_interword_spaces=1x1'

    pages = convert_from_path(filepath, 300)  # Adjust the DPI (resolution) as needed

    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, config=custom_oem_psm_config)
        print(text)


if __name__ == '__main__':
    """"""
    tesseract()
