import os
from PIL import Image
from PyPDF2 import PdfMerger
from PIL import UnidentifiedImageError

def png_to_pdf(png_folder, output_filename):
    # Get all PNG files in the specified folder
    png_files = [f for f in os.listdir(png_folder) if f.endswith('.png') and not f.startswith('._')]
    png_files.sort()  # Sort the files to ensure consistent order

    if not png_files:
        print("No valid PNG files found in the specified folder.")
        return

    # Create a PdfMerger object
    merger = PdfMerger()

    for png_file in png_files:
        # Open the PNG image
        image_path = os.path.join(png_folder, png_file)
        try:
            image = Image.open(image_path)
            
            # Convert the image to RGB mode if it's not already
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Create a temporary PDF file for this image
            pdf_path = f"{png_file.rsplit('.', 1)[0]}.pdf"
            image.save(pdf_path, "PDF", resolution=100.0)
            
            # Append the temporary PDF to the merger
            merger.append(pdf_path)
            
            # Close the image
            image.close()
            
            # Remove the temporary PDF file
            os.remove(pdf_path)
        except UnidentifiedImageError:
            print(f"Skipping unidentified image: {png_file}")
        except Exception as e:
            print(f"Error processing {png_file}: {str(e)}")

    if len(merger.pages) == 0:
        print("No valid images could be processed. PDF was not created.")
        return

    # Write out the merged PDF
    merger.write(output_filename)
    merger.close()

    print(f"PDF created successfully: {output_filename}")


# Usage
png_folder = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts"
output_filename = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Oron Catts/oronCattsFullBook.pdf"
png_to_pdf(png_folder, output_filename)