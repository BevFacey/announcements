# pip install google-auth google-auth-oauthlib google-api-python-client
import os
from datetime import datetime
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request
import pickle

def upload_video():
    client_secrets_file = 'client-secret.json'
    credentials_file = 'youtube-credentials.pkl'
    scopes = ['https://www.googleapis.com/auth/youtube.upload', 'offline']
    video_extension = 'mp4'

    # Find the most recent video file
    video_files = {file: os.path.getctime(file) for file in os.listdir() if file.endswith(video_extension)}
    if not video_files:
        print('No video files found.')
        return
    file_path = max(video_files, key=video_files.get)
    print(f'The most recent video file is: {file_path}')

    # Authenticate to YouTube
    credentials = None
    if os.path.exists(credentials_file):
        with open(credentials_file, 'rb') as token:
            credentials = pickle.load(token)
            print('Credentials loaded from file')

    # Refresh credentials if expired
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing credentials...')
            credentials.refresh(Request())
        else:
            print('Reauthorizing...')
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            flow.redirect_uri = "http://localhost:8080/"
            credentials = flow.run_local_server(port=8080)
            with open(credentials_file, 'wb') as token:
                pickle.dump(credentials, token)

    # Build the YouTube API client
    youtube = build('youtube', 'v3', credentials=credentials)

    # Upload the video
    today = datetime.today()
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": f'Bev Facey Announcements {today.strftime("%Y-%m-%d")} (AI Generated)',
                "description": f'Bev Facey Announcements for {today.strftime("%B %d, %Y")}, generated by AI',
                "tags": ['BevFacey', 'Bev Facey'],
                "categoryId": '27'  # Education
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
    )
    response = request.execute()
    print(f"Video uploaded: https://www.youtube.com/watch?v={response['id']}")

if __name__ == "__main__":
    upload_video()
