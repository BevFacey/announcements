from google.oauth2 import service_account
from googleapiclient.discovery import build
channel_id = 'UCS8NR4uTYkC86rZsnf6LRCA'
service_account_file = 'service-account-file.json'

credentials = service_account.Credentials.from_service_account_file(
    service_account_file,
    scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
)
youtube = build('youtube', 'v3', credentials=credentials)

def get_channel_videos(channel_id):
    request = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    )
    response = request.execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    videos = []
    next_page_token = None
    while True:
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        videos += response['items']
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return videos

videos = get_channel_videos(channel_id)
for video in videos:
    video_title = video['snippet']['title']
    video_id = video['snippet']['resourceId']['videoId']
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    print(f'{video_title}: {video_url}')
