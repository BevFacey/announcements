import os
import requests
import csv
import html
from io import StringIO
import boto3

def synthesize_speech(text, polly_client):
    ssml_text = f'<speak><amazon:domain name="news">{html.escape(text)}</amazon:domain></speak>'
    response = polly_client.synthesize_speech(
        Text=ssml_text, TextType="ssml", OutputFormat="mp3", VoiceId="Joanna", Engine="neural"
    )
    return response["AudioStream"].read()

def fetch_announcements(spreadsheet_key, spreadsheet_gid):
    csv_link = f'https://docs.google.com/spreadsheets/d/{spreadsheet_key}/export?gid={spreadsheet_gid}&format=csv'
    response = requests.get(csv_link)
    response.raise_for_status()
    csv_reader = csv.reader(StringIO(response.text))
    next(csv_reader)  # Skip header row
    return [(row[3], row[4]) for row in csv_reader]

def generate_audio(temp_dir, spreadsheet_key, spreadsheet_gid):
    announcements = fetch_announcements(spreadsheet_key, spreadsheet_gid)
    os.makedirs(temp_dir, exist_ok=True)
    polly_client = boto3.client("polly", region_name="us-west-2")
    audio_files = []
    for i, (title, content) in enumerate(announcements):
        filename = os.path.join(temp_dir, f"{i:02d}_announcement.mp3")
        text_to_speak = content if content.lower().startswith(title.lower()) else f"{title}. {content}"
        with open(filename, "wb") as file:
            file.write(synthesize_speech(text_to_speak, polly_client))
        audio_files.append(filename)
    print(audio_files)
    print(f"{len(audio_files)} audio files generated.")
    return audio_files