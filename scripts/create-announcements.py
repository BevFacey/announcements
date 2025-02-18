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

# Parse CSV content
csv_data = response.text
csv_reader = csv.reader(StringIO(csv_data))
# Skip header row
next(csv_reader)
# Extract announcements, title is in column 3, content in column 4
announcements = [(row[3], row[4]) for row in csv_reader]

# today's date in the format "Month Day, Year"
date_today = date.today().strftime("%B %d, %Y")
print('Good Morning Bev Facey! ',f'Today is {date_today} and here are your morning announcements.')

date_announcement = ('Good Morning Bev Facey! ',f'Today is {date_today} and here are your morning announcements.')
announcements.insert(0, date_announcement)
# if it is Friday, add a land acknowledgement
if date.today().weekday() == 4:
    land_acknowledgement = ('We would like to acknowledge that we are on Treaty 6 territory.', 'A traditional meeting grounds, gathering place, and travelling route to the Cree, Saulteaux, Blackfoot, Métis, Dene, and Nakota Sioux. We acknowledge all the many First Nations, Métis, and Inuit whose footsteps have marked these lands for centuries.')
    announcements.insert(1, land_acknowledgement)
#print(announcements)

############################################ TTS ############################################

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
    

# Save the audio file
announcement_files = []
i = 0
for title, content in announcements:
    print(f"{i} Announcement: {title}")
    filename = f"{i}_announcement.mp3"  # Change file extension to .mp3

    # if the title is the same as the first bit of the content, don't repeat it
    if content.lower().startswith(title.lower()):
        text_to_speak = content
    else:
        text_to_speak = title + '. ' + content
    
    audio = speak(text_to_speak)
    with open(filename, "wb") as file:
        file.write(audio)
    announcement_files.append(filename)
    i += 1

audio = speak("That's all for your morning announcements. Have a great day.")
with open(f"{i}_have_a_great_day.mp3", "wb") as file:
    file.write(audio)

# move the mp3 files to the audio directory
'''
audio_directory = 'audio'
os.makedirs(audio_directory, exist_ok=True)
for file in announcement_files:
    shutil.move(file, os.path.join(audio_directory, file))
'''
    
### Join audio files

# Print the current working directory
print("Current working directory:", os.getcwd())

# find all of the mp3 files in the audio directory
#audio_directory = 'audio'
audio_directory = '.'

announcement_files = [f for f in os.listdir(audio_directory) if f.endswith(".mp3")]
announcement_files.sort()
print(announcement_files)

# Check and print the duration of each mp3 file
for file in announcement_files:
    file_path = os.path.join(audio_directory, file)
    audio = MP3(file_path)
    duration = audio.info.length  # duration in seconds
    print(f"File: {file}, Duration: {duration} seconds")

# Create a half-second silent audio file
if os.path.exists("silence.mp3"):
    os.remove("silence.mp3")
subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", "silence.mp3"])

# Create a text file listing all the mp3 files to be joined
firstFile = True
with open("file_list.txt", "w") as file_list:
    for file in announcement_files:
        file_list.write(f"file '{os.path.join(audio_directory, file)}'\n")
        if not firstFile:
            file_list.write(f"file '{os.path.join(audio_directory, 'silence.mp3')}'\n")
        firstFile = False


output_file = "all_announcements.mp3"
# delete an existing output file
if os.path.exists(output_file):
    os.remove(output_file)
# Use ffmpeg to concatenate the files listed in the text file
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-vf", "apad=pad=0.5", "-c:a", "libmp3lame", output_file])
# Clean up the temporary file list
os.remove("file_list.txt")

print(f"All mp3 files have been joined into {output_file}")

### Download slides

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


### Create video

# Print the current working directory
print("Current working directory:", os.getcwd())
audio_directory = 'audio'
slides_directory = 'slides'

# find all of the mp3 files in the audio directory
announcement_files = [f for f in os.listdir(audio_directory) if f.endswith(".mp3")]
announcement_files.sort()
print(announcement_files)

# Check and print the duration of each mp3 file
durations = {}
for file in announcement_files:
    if file != "all_announcements.mp3" and file != "silence.mp3":
        file_path = os.path.join(audio_directory, file)
        audio = MP3(file_path)
        duration = audio.info.length  # duration in seconds
        durations[file] = duration
        print(f"File: {file}, Duration: {duration} seconds")

# find all of the png files in the slides directory
slide_files = [f for f in os.listdir(slides_directory) if f.endswith(".png")]
slide_files.sort()
print(slide_files)

# Create a temporary directory to store the images with the correct durations
temp_dir = 'temp_slides'
os.makedirs(temp_dir, exist_ok=True)

# Save each slide with the correct duration
for i, slide_file in enumerate(slide_files):
    slide_path = os.path.join(slides_directory, slide_file)
    slide_image = Image.open(slide_path)
    slide_duration = durations[announcement_files[i]]
    temp_slide_path = os.path.join(temp_dir, f'{i}_slide.png')
    slide_image.save(temp_slide_path)
    # Create a video segment for each slide
    subprocess.run(["ffmpeg", "-loop", "1", "-i", temp_slide_path, "-c:v", "libx264", "-t", str(slide_duration), "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080", os.path.join(temp_dir, f'{i}_slide.mp4')])

# Concatenate all the video segments
with open(os.path.join(temp_dir, "file_list.txt"), "w") as file_list:
    for i in range(len(slide_files)):
        file_list.write(f"file '{i}_slide.mp4'\n")

# Use ffmpeg to combine the video segments and audio into a final video
output_file = "morning_announcements.mp4"
# delete an existing output file
if os.path.exists(output_file):
    os.remove(output_file)
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", os.path.join(temp_dir, "file_list.txt"), "-i", os.path.join(audio_directory, "all_announcements.mp3"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-strict", "experimental", "-shortest", output_file])

# Clean up the temporary files
shutil.rmtree(temp_dir)

print(f"Video created: {output_file}")
