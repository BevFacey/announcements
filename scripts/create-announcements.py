import requests
import csv
from io import StringIO
from datetime import date
import html

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
date_announcement = ('Good Morning Bev Facey! ',f'Today is {date_today} and here are your morning announcements.')
announcements.insert(0, date_announcement)
# if it is Friday, add a land acknowledgement
if date.today().weekday() == 4:
    land_acknowledgement = ('We would like to acknowledge that we are on Treaty 6 territory.', 'A traditional meeting grounds, gathering place, and travelling route to the Cree, Saulteaux, Blackfoot, Métis, Dene, and Nakota Sioux. We acknowledge all the many First Nations, Métis, and Inuit whose footsteps have marked these lands for centuries.')
    announcements.insert(1, land_acknowledgement)
#print(announcements)

############################################ TTS ############################################

import boto3
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
import os
import shutil
audio_directory = 'audio'
os.makedirs(audio_directory, exist_ok=True)
for file in announcement_files:
    shutil.move(file, os.path.join(audio_directory, file))