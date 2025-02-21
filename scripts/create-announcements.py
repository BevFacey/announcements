# pip install requests, boto3, mut, Pillow, pdf2image, mutagen
# sudo apt-get install ffmpeg

import requests
import csv
from io import StringIO
from datetime import date
import html
import os
import shutil
import subprocess
from mutagen.mp3 import MP3
from pdf2image import convert_from_path
from PIL import Image
import boto3

spreadsheet_key = '1SV4eWy58Y6iEIIOGUH60xUZV59eaY7ewp4EoeCZzNxc'
spreadsheet_gid = '1783949168'
csv_link = 'https://docs.google.com/spreadsheets/d/'+spreadsheet_key+'/export?gid='+spreadsheet_gid+'&format=csv'
response = requests.get(csv_link)
response.raise_for_status()  # Ensure the request was successful
csv_data = response.text
csv_reader = csv.reader(StringIO(csv_data))
next(csv_reader) # Skip header row
# Extract announcements, title is in column 3, content in column 4
announcements = [(row[3], row[4]) for row in csv_reader]

# today's date in the format "Month Day, Year"
date_today = date.today().strftime("%B %d, %Y")
date_announcement = ('Good Morning Bev Facey! ',f'Today is {date_today} and here are your morning announcements.')
#print(date_announcement)
announcements.insert(0, date_announcement)
if date.today().weekday() == 4:  # if it is Friday, add a land acknowledgement
    land_acknowledgement = ('We would like to acknowledge that we are on Treaty 6 territory.', 'A traditional meeting grounds, gathering place, and travelling route to the Cree, Saulteaux, Blackfoot, Métis, Dene, and Nakota Sioux. We acknowledge all the many First Nations, Métis, and Inuit whose footsteps have marked these lands for centuries.')
    announcements.insert(1, land_acknowledgement)

# add a closing announcement
announcements.append(("That's all for your morning announcements.", "Have a great day."))
print(announcements)

temp_dir = 'temporary_directory'
os.makedirs(temp_dir, exist_ok=True)

### TTS ###

# credentials are stored in ~/.aws/credentials
polly_client = boto3.client("polly", region_name="us-west-2")

def speak(announcement):
    ssml_text = '<speak><amazon:domain name="news">' + html.escape(announcement) + '</amazon:domain></speak>'
    response = polly_client.synthesize_speech(
        Text=ssml_text,
        TextType="ssml",  # Tells Polly we're using SSML
        OutputFormat="mp3",
        VoiceId="Joanna",  # demos at https://sreyseng.medium.com/amazon-polly-text-to-speech-tts-voice-samples-en-8282e5c7ba28
        Engine="neural"  # Required for newscaster style
    )
    return response["AudioStream"].read()

audio_files = []

# Save the audio file
i = 0
for title, content in announcements:
    print(f"{i} Announcement: {title}")
    filename = f"{i}_announcement.mp3"
    audio_files.append(filename)

    # if the title is the same as the first bit of the content, don't repeat it
    if content.lower().startswith(title.lower()):
        text_to_speak = content
    else:
        text_to_speak = title + '. ' + content
    
    audio = speak(text_to_speak)
    with open(filename, "wb") as file:
        file.write(audio)
    i += 1

audio = speak()
closing_file = f"{i}_have_a_great_day.mp3"
with open(closing_file, "wb") as file:
    file.write(audio)
audio_files.append(closing_file)
    
# move the mp3 files to the temp directory
for file in audio_files:
    shutil.move(file, os.path.join(temp_dir, file))

# join audio files

# Check and print the duration of each mp3 file
for file in audio_files:
    file_path = os.path.join(temp_dir, file)
    audio = MP3(file_path)
    duration = audio.info.length  # duration in seconds
    print(f"File: {file}, Duration: {duration} seconds")

# Create a half-second silent audio file if it doesn't exist in the temp_dir 
if not os.path.exists(os.path.join(temp_dir, "silence.mp3")):
    subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", os.path.join(temp_dir, "silence.mp3")])

output_file = os.path.join(temp_dir, "all_announcements.mp3")
if os.path.exists(os.path.join(output_file)):
    os.remove( output_file)

# Create a text file listing all the mp3 files to be joined
with open("file_list.txt", "w") as file_list:
    for file in audio_files:
        file_list.write(f"file '{os.path.join(temp_dir, file)}'\n")

# Use ffmpeg to concatenate the files listed in the text file
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-vf", "apad=pad=0.5", "-c:a", "libmp3lame", output_file])
os.remove("file_list.txt")

### Download slides as a PDF file and export to PNG ###

presentation_id = '1Bdwl1ucbFGd1qDrZk-D3o6uN0S_LyN3TQ75kOd4wiGo'
pdf_url = f'https://docs.google.com/presentation/d/{presentation_id}/export/pdf'
pdf_response = requests.get(pdf_url)
pdf_filename = 'slides.pdf'
with open(pdf_filename, 'wb') as pdf_file:
    pdf_file.write(pdf_response.content)
print(f'Presentation downloaded as {pdf_filename}')

# Convert the PDF file to PNG images
os.makedirs(temp_dir, exist_ok=True)
images = convert_from_path(pdf_filename)
for i, image in enumerate(images):
    image_filename = os.path.join(temp_dir, f'{i}_slide.png')
    image.thumbnail((1920, 1080))  # resize to 1920x1080
    image.save(image_filename, 'PNG')
    print(f'Slide {i + 1} saved as {image_filename}')

### Create video ###

# Check and print the duration of each mp3 file
durations = {}
for file in audio_files:
    if file != "all_announcements.mp3" and file != "silence.mp3":
        file_path = os.path.join(temp_dir, file)
        audio = MP3(file_path)
        duration = audio.info.length  # duration in seconds
        durations[file] = duration
        print(f"File: {file}, Duration: {duration} seconds")

# find all of the png files in the slides directory
slide_files = [f for f in os.listdir(temp_dir) if f.endswith(".png")]
slide_files.sort()

# Store the images with the correct durations
for j, slide_file in enumerate(slide_files):
    slide_path = os.path.join(temp_dir, slide_file)
    slide_image = Image.open(slide_path)
    slide_duration = durations[audio_files[j]]
    temp_slide_path = os.path.join(temp_dir, f'{j}_slide.png')
    slide_image.save(temp_slide_path)
    # Create a video segment for each slide
    subprocess.run(["ffmpeg", "-loop", "1", "-i", temp_slide_path, "-c:v", "libx264", "-t", str(slide_duration), "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080", os.path.join(temp_dir, f'{i}_slide.mp4')])

# Concatenate all the video segments
with open(os.path.join(temp_dir, "file_list.txt"), "w") as file_list:
    for i in range(len(slide_files)):
        file_list.write(f"file '{i}_slide.mp4'\n")

# Use ffmpeg to combine the video segments and audio into a final video
date_today_iso = date.today().isoformat()
output_file = f"Bev Facey Announcements {date_today_iso}.mp4"
if os.path.exists(output_file):
    os.remove(output_file)
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", os.path.join(temp_dir, "file_list.txt"), "-i", os.path.join(audio_directory, "all_announcements.mp3"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-strict", "experimental", "-shortest", output_file])

# Clean up the temporary files
shutil.rmtree(temp_dir)
# delete the pdf file
os.remove(pdf_filename)

print(f"Video created: {output_file}")
