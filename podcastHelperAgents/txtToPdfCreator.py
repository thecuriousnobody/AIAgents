import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def read_file_with_fallback_encoding(file_path, encodings=['utf-8', 'latin-1', 'cp1252']):
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError(f"Unable to decode the file {file_path} with any of the attempted encodings.")

def txt_files_to_pdf(input_directory, output_filename):
    # Create a PDF document
    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Get all .txt files in the directory
    txt_files = [f for f in os.listdir(input_directory) if f.endswith('.txt')]
    
    # Sort the files alphabetically
    txt_files.sort()

    # Process each .txt file
    for txt_file in txt_files:
        file_path = os.path.join(input_directory, txt_file)
        
        # Add the filename as a header
        story.append(Paragraph(txt_file, styles['Heading1']))
        story.append(Spacer(1, 12))
        
        # Read and add content of the .txt file
        try:
            content = read_file_with_fallback_encoding(file_path)
            for line in content.splitlines():
                story.append(Paragraph(line.strip(), styles['Normal']))
            story.append(Spacer(1, 12))
        except UnicodeDecodeError as e:
            print(f"Error reading file {txt_file}: {str(e)}")
            story.append(Paragraph(f"Error reading file: {txt_file}", styles['Normal']))
        
        # Add a page break after each file
        story.append(Paragraph('<para style="page-break-after: always"></para>', styles['Normal']))

    # Build the PDF
    doc.build(story)
    print(f"PDF created successfully: {output_filename}")

#
# Usage
input_dir = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Varnika Singh/YouTube Transcripts"  # Replace with your directory path
output_pdf = "/Volumes/Samsung/digitalArtifacts/podcastPrepDocuments/Varnika Singh/YouTube Transcripts/combined_output.pdf"  # Name of the output PDF file

txt_files_to_pdf(input_dir, output_pdf)