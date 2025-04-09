from datetime import date
import csv
import base64
from hume import HumeClient
from hume.tts import PostedUtterance
import os

def create_audio():
    with open("text_data.csv", "r", encoding="utf-8") as file:
        csv_reader = csv.reader(file)
        announcements = list(csv_reader)
    print(f"{len(announcements)} announcements loaded.")
    date_today = date.today().strftime("%B %d, %Y")
    announcements.insert(0, ['Good Morning Bev Facey',f'Today is {date_today} and here are your morning announcements.'])
    if date.today().weekday() == 4:  # if it is Friday, add a land acknowledgement
        land_acknowledgement = ['We would like to acknowledge that we are on Treaty 6 territory.', 'A traditional meeting grounds, gathering place, and travelling route to the Cree, Saulteaux, Blackfoot, Métis, Dene, and Nakota Sioux. We acknowledge all the many First Nations, Métis, and Inuit whose footsteps have marked these lands for centuries.']
        announcements.insert(1, land_acknowledgement)
    announcements.append(["That's all for your morning announcements", "Have a great day."])
    
    with open("hume_keys.txt", "r") as file:
        lines = file.readlines()
        api_key = lines[0].strip()
    hume = HumeClient(api_key=api_key)

    for i, (title, content) in enumerate(announcements):
        filename = f"{i:02d}_announcement.mp3"
        text = content if content.lower().startswith(title.lower()) else f"{title}. {content}"
        print(text)
        print('---')
        #if i>7:
        if True:
            speech1 = hume.tts.synthesize_json(
                utterances=[
                    PostedUtterance(
                        description='A young Canadian news anchor',
                        text=text,
                        trailing_silence=0.5,
                    )
                ]
            )
            audio_data = base64.b64decode(speech1.generations[0].audio)
            with open(filename, "wb") as f:
                f.write(audio_data)
            print("Wrote", filename)
    print(f"{len(announcements)} audio files generated.")
    os.remove('text_data.csv')

if __name__ == "__main__":
    create_audio()