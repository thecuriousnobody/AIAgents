import os
import sys
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

# Set the path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'

def pdf_to_text(pdf_path, output_path, dpi=200, chunk_size=10):
    def process_chunk(start_page, end_page):
        try:
            pages = convert_from_path(pdf_path, dpi, first_page=start_page, last_page=end_page, poppler_path="/opt/homebrew/bin")
            text = ""
            for page in pages:
                text += pytesseract.image_to_string(page)
            return text
        except Exception as e:
            print(f"Error processing pages {start_page} to {end_page}: {str(e)}")
            return ""

    try:
        total_pages = len(convert_from_path(pdf_path, dpi, poppler_path="/opt/homebrew/bin"))
        
        with open(output_path, 'w') as f:
            for i in range(1, total_pages + 1, chunk_size):
                chunk_text = process_chunk(i, min(i + chunk_size - 1, total_pages))
                f.write(chunk_text)
                print(f"Processed pages {i} to {min(i + chunk_size - 1, total_pages)}")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        sys.exit(1)

# Usage
pdf_path = '/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/oronCattsFullBook.pdf'
output_path = '/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/output.txt'

try:
    pdf_to_text(pdf_path, output_path)
    print("OCR process completed. Check output.txt for results.")
except Exception as e:
    print(f"An error occurred: {str(e)}")
    sys.exit(1)

# Usage

