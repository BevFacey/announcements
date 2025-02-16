apikey = ""

from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key=apikey)

def create_speech(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = client.audio.speech.create(
        model="tts-1-hd", # high quality than tts-1 but slower
        voice="shimmer", # can also try echo or sage
        input=text,
    )
    #response.stream_to_file(speech_file_path)
    
    # save the audio to a file
    with open(speech_file_path, "wb") as f:
        f.write(response.audio)

text = "Good morning, Bev Facey. This is a test of OpenAI text to speech!"
create_speech(text)