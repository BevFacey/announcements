from datetime import date
import os
import subprocess
from mutagen.mp3 import MP3

def create_video():
    slide_files = [file for file in os.listdir('.') if file.endswith('.png')]
    audio_files = [file for file in os.listdir('.') if file.endswith('.mp3')]
    if len(slide_files) != len(audio_files):
        print('Error: Number of slides does not match number of audio files')
        print(f'Slide files: {len(slide_files)} and audio files: {len(audio_files)}')
        return False
    slide_files.sort()
    audio_files.sort()
   
    video_segments = []
    for i in range(len(slide_files)):
        video_file_name = f'{i:02d}_video.mp4'
        if os.path.exists(video_file_name):
            os.remove(video_file_name)
        audio_duration = MP3(audio_files[i]).info.length
        subprocess.run([
            "ffmpeg", "-loop", "1", "-framerate", "30", "-i", slide_files[i], "-i", audio_files[i], "-c:v", "libx264", "-c:a", "aac",
            "-strict", "experimental", "-b:a", "192k", "-t", str(audio_duration), "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080", video_file_name
        ])
        video_segments.append(video_file_name)
    
    video_files_txt_path = 'video_files.txt'
    with open(video_files_txt_path, "w") as video_files_txt:
        for segment in video_segments:
            video_files_txt.write(f"file '{segment}'\n")

    print('joining video segments')
    date_today_iso = date.today().isoformat()
    video_output_file = f"Bev Facey Announcements {date_today_iso} (AI Generated).mp4"
    if os.path.exists(video_output_file):
        os.remove(video_output_file)
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", video_files_txt_path, "-c", "copy", "-fflags", "+genpts", video_output_file
    ])

    os.remove(video_files_txt_path)
    print(f'Video created: {video_output_file}')
    for file in slide_files + audio_files + video_segments:
        os.remove(file)
    return True
        
if __name__ == "__main__":
    create_video()