import googleapiclient.discovery
import googleapiclient.errors
import json
from datetime import datetime
import isodate
import os
import webbrowser
import pyautogui
import time
import socket

def get_latest_video(channel_username):
    """
    Gets the most recent video from a YouTube channel by username
    Returns the video ID of the most recent upload
    """
    # YouTube API setup
    api_service_name = "youtube"
    api_version = "v3"
    
    # Read API key from client-secret.json
    try:
        with open('client-secret-read.json', 'r') as f:
            secret_data = json.load(f)
            api_key = secret_data.get('api_key')
            
        if not api_key:
            print("Error: 'api_key' not found in client-secret.json")
            return None
    except FileNotFoundError:
        print("Error: client-secret-read.json file not found")
        return None
    except json.JSONDecodeError:
        print("Error: client-secret-read.json is not valid JSON")
        return None
    
    # Create YouTube API client
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=api_key)
    
    # First, get the channel ID from the username handle
    request = youtube.search().list(
        part="snippet",
        q=channel_username,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    
    if not response.get('items'):
        print(f"No channel found with username: {channel_username}")
        return None
    
    channel_id = response['items'][0]['id']['channelId']
    
    # Get the uploads playlist ID for the channel
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )
    response = request.execute()
    
    if not response.get('items'):
        print(f"No channel found with ID: {channel_id}")
        return None
    
    # Get the uploads playlist ID
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    
    # Get the most recent video from the uploads playlist
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=1
    )
    response = request.execute()
    
    if not response.get('items'):
        print(f"No videos found in channel: {channel_username}")
        return None
    
    # Get the video ID
    video_id = response['items'][0]['contentDetails']['videoId']
    video_title = response['items'][0]['snippet']['title']
    publish_time = response['items'][0]['snippet']['publishedAt']
    
    # Get video duration
    request = youtube.videos().list(
        part="contentDetails",
        id=video_id
    )
    response = request.execute()
    
    if not response.get('items'):
        print(f"Could not fetch details for video: {video_id}")
        return None
    
    # Extract duration (ISO 8601 format)
    iso_duration = response['items'][0]['contentDetails']['duration']
    
    # Convert duration to human-readable format (HH:MM:SS)
    duration_timedelta = isodate.parse_duration(iso_duration)
    duration_seconds = int(duration_timedelta.total_seconds())
    #duration_str = str(timedelta(seconds=duration_seconds))
    print(f"Duration: {duration_seconds} seconds")

    return {
        'video_id': video_id,
        'title': video_title,
        'published_at': publish_time,
        'duration': duration_seconds
    }

def create_html_page(video_info):
    """
    Creates an HTML page that embeds the YouTube video in fullscreen
    """
    if not video_info:
        return None
    
    video_id = video_info['video_id']
    video_title = video_info['title']
    published_date = datetime.fromisoformat(video_info['published_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bev Facey Announcements - Latest Video</title>
    <style>
        body, html {{
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background-color: #000;
        }}
        .container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
        }}
        .video-info {{
            color: white;
            padding: 10px;
            background-color: #0f0f0f;
        }}
        .video-container {{
            flex-grow: 1;
            width: 100%;
            height: calc(100% - 60px);
        }}
        iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="video-container">
            <iframe 
                src="https://www.youtube.com/embed/{video_id}?autoplay=1&fs=1&mute=0"
                frameborder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                allowfullscreen>
            </iframe>
        </div>
    </div>
</body>
</html>"""
    
    # Write the HTML content to a file
    with open("latest_video.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"HTML page created: latest_video.html")
    print(f"Latest video: {video_title} (Published on: {published_date})")
    
    return "latest_video.html"

def hdmi_input(destination):
    """
    Switches the HDMI input
    Takes in the destination as an integer
    1 : HDMI 1
    2 : HDMI 2
    3 : HDMI 3
    """
    UDP_IP = '192.168.140.25'  # VP-440 IP address (default)
    UDP_PORT = 50000         # VP-440 UDP port (default)
    command = '#ROUTE 12,1,' + str(int(destination)-1) + '\r'
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(command.encode(), (UDP_IP, UDP_PORT))
    sock.close()

def main():
    # YouTube channel username/handle
    channel_username = "bevfaceyannouncements"
    
    print(f"Fetching the latest video from {channel_username}...")
    video_info = get_latest_video(channel_username)
    
    if video_info:
        html_file = create_html_page(video_info)
        if html_file:
            webbrowser.open(f"file://{os.path.realpath(html_file)}")
            time.sleep(5) # wait for the page to load
            screen_width, screen_height = pyautogui.size()
            hdmi_input(3) # switch to laptop
            pyautogui.click(screen_width // 2, screen_height // 2)
            time.sleep(1)
            pyautogui.press('f') # press 'f' to enter fullscreen
            time.sleep(video_info['duration'] + 3) # wait for the video to finish
            hdmi_input(1) # switch back to BrightSign
            pyautogui.press('esc')
            pyautogui.hotkey('ctrl', 'w') # close the browser tab (assuming that it is Chrome on Windows)
            #os.remove(html_file)
    else:
        print("Failed to get the latest video information.")

if __name__ == "__main__":
    main()