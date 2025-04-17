import requests
from time import sleep
from download_text import download_text
from download_slides import download_slides
#from create_audio import create_audio
from create_audio_amazon import create_audio
from create_video import create_video
from upload_video import upload_video

# update the spreadsheet and slides online
r = requests.get('https://script.google.com/macros/s/AKfycbyn5y-tbC8DYHpahMnrFgE_KPxuG-M2Q5f5N7IhfRWUevl5akfLNWSFVZsIeptXTMCt/exec')
sleep(3)
r = requests.get('https://script.google.com/macros/s/AKfycbyn5y-tbC8DYHpahMnrFgE_KPxuG-M2Q5f5N7IhfRWUevl5akfLNWSFVZsIeptXTMCt/exec')
if r.status_code == 200:
    sleep(5) # wait for the slides to be updated
    download_text()
    download_slides()
    create_audio()
    v = create_video()
    if v:
        upload_video()
    else:
        print('Video creation failed.')
else:
    print('Failed to update the slides online.')

print('Process completed.')
