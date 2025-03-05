import os
from datetime import date
from generate_audio import generate_audio
from download_slides import download_and_convert_slides
from create_video import create_video
from upload_youtube import upload_video

TEMP_DIR = 'temporary_directory'
SHEET_KE = '1SV4eWy58Y6iEIIOGUH60xUZV59eaY7ewp4EoeCZzNxc'
SHEET_GID = '1783949168'
PRESENTATION_ID = '1Bdwl1ucbFGd1qDrZk-D3o6uN0S_LyN3TQ75kOd4wiGo'

os.makedirs(TEMP_DIR, exist_ok=True)
slide_files = download_and_convert_slides(PRESENTATION_ID, TEMP_DIR)
audio_files = generate_audio(TEMP_DIR)

date_today_iso = date.today().isoformat()
video_output_file = f"Bev Facey Announcements {date_today_iso} (AI Generated).mp4"
create_video(slide_files, audio_files, TEMP_DIR, video_output_file)

upload_video(video_output_file)

os.rmdir(TEMP_DIR)
print('Process completed successfully.')
