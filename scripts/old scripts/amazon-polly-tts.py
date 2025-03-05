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

ssml_text = """
<speak>
    <amazon:domain name="news">
        Good morning, Bev Facey! This is a test of Amazon Polly's newscaster style.
    </amazon:domain>
</speak>
"""
response = polly_client.synthesize_speech(
    Text=ssml_text,
    TextType="ssml",  # Tells Polly we're using SSML
    OutputFormat="mp3",
    VoiceId="Joanna",
    Engine="neural"  # Required for newscaster style
)

# Save the audio file
with open("newscaster_speech.mp3", "wb") as file:
    file.write(response["AudioStream"].read())

print("Speech saved as speech.mp3")
