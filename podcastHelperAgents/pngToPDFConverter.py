import os
from PIL import Image
from PyPDF2 import PdfMerger
from PIL import UnidentifiedImageError

def png_to_pdf(png_folder, output_path):
    print(f"Input folder: {png_folder}")
    print(f"Output path: {output_path}")
    print(f"Folder exists: {os.path.exists(png_folder)}")

    # Verify input folder exists
    if not os.path.exists(png_folder):
        print(f"Error: Input folder '{png_folder}' does not exist.")
        return

    # Get all PNG files in the specified folder
    png_files = [f for f in os.listdir(png_folder) if f.lower().endswith('.png') and not f.startswith('._')]
    png_files.sort()  # Sort the files to ensure consistent order

    if not png_files:
        print("No valid PNG files found in the specified folder.")
        return

    print(f"Found {len(png_files)} PNG files")

    # Create a PdfMerger object
    merger = PdfMerger()

    # Ensure the output path has .pdf extension
    if not output_path.lower().endswith('.pdf'):
        output_path += '.pdf'

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Create temporary directory for intermediate PDFs
    temp_dir = os.path.join(output_dir, 'temp_pdfs')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    try:
        for png_file in png_files:
            # Open the PNG image
            image_path = os.path.join(png_folder, png_file)
            try:
                print(f"Processing: {png_file}")
                image = Image.open(image_path)
                
                # Convert the image to RGB mode if it's not already
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Create a temporary PDF file for this image
                temp_pdf = os.path.join(temp_dir, f"temp_{png_file}.pdf")
                image.save(temp_pdf, "PDF", resolution=100.0)
                
                # Append the temporary PDF to the merger
                merger.append(temp_pdf)
                
                # Close the image
                image.close()
                print(f"Successfully processed: {png_file}")
            except UnidentifiedImageError:
                print(f"Skipping unidentified image: {png_file}")
            except Exception as e:
                print(f"Error processing {png_file}: {str(e)}")

        if len(merger.pages) == 0:
            print("No valid images could be processed. PDF was not created.")
            return

        # Write out the merged PDF
        print(f"Creating final PDF: {output_path}")
        merger.write(output_path)
        merger.close()

        print(f"PDF created successfully: {output_path}")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise
    finally:
        # Clean up temporary files
        for file in os.listdir(temp_dir):
            try:
                os.remove(os.path.join(temp_dir, file))
            except:
                pass
        try:
            os.rmdir(temp_dir)
        except:
            pass

if __name__ == "__main__":
    # Get input from user
    png_folder = input("Enter the path of the folder containing PNGs: ")
    output_path = input("Enter the path for the output PDF file: ")
    
    try:
        png_to_pdf(png_folder, output_path)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        exit(1)
