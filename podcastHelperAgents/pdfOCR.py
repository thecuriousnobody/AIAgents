import os
import sys
import subprocess
import fitz  # PyMuPDF
import pytesseract
from PIL import Image

print("Python version:", sys.version)
print("PyMuPDF version:", fitz.__version__)
print("Pytesseract version:", pytesseract.__version__)
print("Current working directory:", os.getcwd())

# Find Tesseract path
tesseract_path = "/usr/local/bin/tesseract"  # Hardcoding the path we know is correct
pytesseract.pytesseract.tesseract_cmd = tesseract_path
print(f"Tesseract command: {tesseract_path}")

# Check Tesseract version
try:
    tesseract_version = subprocess.check_output([tesseract_path, '--version']).decode()
    print("Tesseract version:")
    print(tesseract_version)
except subprocess.CalledProcessError as e:
    print(f"Error running tesseract: {e}")

print("PATH:")
print(os.environ['PATH'])

def ensure_absolute_path(path):
    """Ensure the path is an absolute path starting with /"""
    if not path.startswith('/'):
        # If path starts with Users, assume it's from root
        if path.startswith('Users/'):
            return '/' + path
    return path

def pdf_to_text(pdf_path, output_path, dpi=200):
    # Ensure absolute paths
    pdf_path = ensure_absolute_path(pdf_path)
    output_path = ensure_absolute_path(output_path)

    print(f"Processing PDF: {pdf_path}")
    print(f"Output path: {output_path}")
    print(f"PDF exists: {os.path.exists(pdf_path)}")

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    try:
        doc = fitz.open(pdf_path)
        total_pages = len(doc)
        print(f"Total pages: {total_pages}")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for page_num in range(total_pages):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                text = pytesseract.image_to_string(img)
                f.write(f"\n=== Page {page_num + 1} ===\n\n")
                f.write(text)
                print(f"Processed page {page_num + 1}")
        
        print("OCR process completed. Check output file for results.")
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        raise

if __name__ == "__main__":
    print("\nPlease provide absolute paths starting from the root directory (/)")
    print("Example: /Users/username/Documents/file.pdf\n")
    
    # Get input from user
    pdf_path = input("Enter the path to the PDF file: ")
    output_path = input("Enter the path for the output text file: ")

    # Add .txt extension if not present
    if not output_path.lower().endswith('.txt'):
        output_path += '.txt'

    try:
        pdf_to_text(pdf_path, output_path)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        sys.exit(1)
