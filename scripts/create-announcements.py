import requests
import csv
from io import StringIO

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
#print(announcements)

############################################ TTS ############################################

import boto3
# credentials are stored in ~/.aws/credentials
polly_client = boto3.client("polly", region_name="us-west-2")

ssml_text = """
<speak>
    <amazon:domain name="news">
        Good morning, Bev Facey! This is a test of Amazon Polly's newscaster style.
    </amazon:domain>
</speak>
"""

import boto3
# credentials are stored in ~/.aws/credentials
polly_client = boto3.client("polly", region_name="us-west-2")

'''
# Convert text to speech
response = polly_client.synthesize_speech(
    Text="Good morning, Bev Facey!",
    OutputFormat="mp3",
    VoiceId="Joanna"  # use voice Joanna as newscaster https://sreyseng.medium.com/amazon-polly-text-to-speech-tts-voice-samples-en-8282e5c7ba28
)
'''

def speak(announcement):
    ssml_text = '<speak><amazon:domain name="news">' + announcement + '</amazon:domain></speak>'
    response = polly_client.synthesize_speech(
        Text=ssml_text,
        TextType="ssml",  # Tells Polly we're using SSML
        OutputFormat="mp3",
        VoiceId="Joanna",  # demos at https://sreyseng.medium.com/amazon-polly-text-to-speech-tts-voice-samples-en-8282e5c7ba28
        Engine="neural"  # Required for newscaster style
    )
    return response["AudioStream"].read()

# Save the audio file
#with open("newscaster_speech.mp3", "wb") as file:
#    file.write(response["AudioStream"].read())

announcement_files = []
i = 1
for title, content in announcements:
    print(f"Announcement {i}: {title}")
    filename = f"announcement_{i}.mp3"
    audio = speak(title + content)
    with open(filename, "wb") as file:
        file.write(audio)
    announcement_files.append(filename)
    i += 1


# join the audio files together into one file
#import pydub
from pydub import AudioSegment
from pydub.playback import play

announcement_audio = sum([AudioSegment.from_file(file) for file in announcement_files])
announcement_audio.export("all_announcements.mp3", format="mp3")


