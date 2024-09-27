# pip install google-auth google-auth-oauthlib google-api-python-client
import os
import glob
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
SERVICE_ACCOUNT_FILE = 'service-account-file.json'
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']
video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']

def upload_video(file_path):
    today = datetime.today()
    credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f'Bev Facey Announcements {today.strftime("%Y-%m-%d")}',
                "description": f'Bev Facey Announcements for {today.strftime("%B %d, %Y")}',
                "tags": ['BevFacey', 'Bev Facey'],
                "categoryId": '27' # Education
            },
            "status": {
                "privacyStatus": "public"
                #"privacyStatus": "private"
            }
        },
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    response = request.execute()
    print(f"Video uploaded: {response['id']}")

video_files = []
for ext in video_extensions:
    video_files.extend(glob.glob(ext))
if not video_files:
    print('No video files found.')
else:
    most_recent_video = max(video_files, key=os.path.getctime)
    print(f'The most recent video file is: {most_recent_video}')
    upload_video(file_path=most_recent_video)