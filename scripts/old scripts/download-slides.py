import requests
import os
from pdf2image import convert_from_path

# Download the presentation as a PDF file
presentation_id = '1Bdwl1ucbFGd1qDrZk-D3o6uN0S_LyN3TQ75kOd4wiGo'
pdf_url = f'https://docs.google.com/presentation/d/{presentation_id}/export/pdf'
pdf_response = requests.get(pdf_url)
pdf_filename = 'presentation.pdf'
with open(pdf_filename, 'wb') as pdf_file:
    pdf_file.write(pdf_response.content)
print(f'Presentation downloaded as {pdf_filename}')

# Convert the PDF file to PNG images
output_dir = 'slides'
os.makedirs(output_dir, exist_ok=True)
images = convert_from_path(pdf_filename)
for i, image in enumerate(images):
    image_filename = os.path.join(output_dir, f'{i}_slide.png')
    # resize to 1920x1080
    image.thumbnail((1920, 1080))
    image.save(image_filename, 'PNG')
    print(f'Slide {i + 1} saved as {image_filename}')

print('All slides converted to PNG images.')