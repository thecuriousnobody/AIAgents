from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def pdf_to_text(pdf_path):
    pages = convert_from_path(pdf_path, 500, poppler_path="/opt/homebrew/bin")
    text = ""
    for page in pages:
        text += pytesseract.image_to_string(page)
    return text

# Usage
pdf_text = pdf_to_text('/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/oronCattsFullBook.pdf')
with open('/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/oronCattsFullBook.txt') as f:
    f.write(pdf_text)