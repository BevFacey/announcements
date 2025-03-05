import os
import requests
from pdf2image import convert_from_path

def download_and_convert_slides(presentation_id, temp_dir):
    pdf_url = f'https://docs.google.com/presentation/d/{presentation_id}/export/pdf'
    pdf_filename = os.path.join(temp_dir, 'slides.pdf')
    os.makedirs(temp_dir, exist_ok=True)
    
    pdf_response = requests.get(pdf_url)
    with open(pdf_filename, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f'Presentation downloaded as {pdf_filename}')
    
    images = convert_from_path(pdf_filename)
    slide_files = []
    for i, image in enumerate(images):
        image_filename = os.path.join(temp_dir, f'{i:02d}_slide.png')
        image.thumbnail((1920, 1080))
        image.save(image_filename, 'PNG')
        slide_files.append(image_filename)
        print(f'Slide {i + 1} saved as {image_filename}')
    
    os.remove(pdf_filename)
    return slide_files