# pip install google-auth google-auth-oauthlib google-api-python-client
import os
import glob
from datetime import datetime
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

channel_id = 'UCS8NR4uTYkC86rZsnf6LRCA'
client_secrets_file = 'client-secret.json'
credentials_file = 'youtube-credentials.pkl'
scopes = ['https://www.googleapis.com/auth/youtube.upload']
video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv']

def upload_video(file_path):
    credentials = None
    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as token:
            credentials = pickle.load(token)
    if not credentials or not credentials.valid:
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
        flow.redirect_uri = "http://localhost:8080/"
        credentials = flow.run_local_server(port=8080)
        with open(credentials_file, 'wb') as token:
            pickle.dump(credentials, token)
    youtube = build('youtube', 'v3', credentials=credentials)

    today = datetime.today()
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

def upload_video_not_working(file_path):
    today = datetime.today()
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = build('youtube', 'v3', credentials=credentials)
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f'Bev Facey Announcements {today.strftime("%Y-%m-%d")}',
                "description": f'Bev Facey Announcements for {today.strftime("%B %d, %Y")}',
                "tags": ['BevFacey', 'Bev Facey'],
                "categoryId": '27', # Education
                "channelId": channel_id
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