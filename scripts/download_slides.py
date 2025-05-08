import requests
import os
from pdf2image import convert_from_path

def download_slides():
    presentation_id = '1Bdwl1ucbFGd1qDrZk-D3o6uN0S_LyN3TQ75kOd4wiGo'
    pdf_url = f'https://docs.google.com/presentation/d/{presentation_id}/export/pdf'
    pdf_filename = 'slides.pdf'
    pdf_response = requests.get(pdf_url)
    with open(pdf_filename, 'wb') as pdf_file:
        pdf_file.write(pdf_response.content)
    print(f'Presentation downloaded as {pdf_filename}')
    
    images = convert_from_path(pdf_filename)
    for i, image in enumerate(images):
        image_filename = f'{i:02d}_slide.png'
        image.thumbnail((1920, 1080))
        image.save(image_filename, 'PNG')
        print(f'Slide {i + 1} saved as {image_filename}')
    
    os.remove(pdf_filename)

if __name__ == "__main__":
    r = requests.get('https://script.google.com/macros/s/AKfycbyn5y-tbC8DYHpahMnrFgE_KPxuG-M2Q5f5N7IhfRWUevl5akfLNWSFVZsIeptXTMCt/exec')
    download_slides()