import os
import subprocess
from PIL import Image
from mutagen.mp3 import MP3

def create_video(slide_files, audio_files, temp_dir, output_file):
    durations = {file: MP3(os.path.join(temp_dir, file)).info.length for file in audio_files if file.endswith(".mp3")}
    
    video_segments = []
    for j, slide_file in enumerate(slide_files):
        slide_path = os.path.join(temp_dir, slide_file)
        slide_duration = durations.get(audio_files[j], 5)  # Default to 5 seconds
        video_file_name = os.path.join(temp_dir, f'{j:02d}_slide.mp4')
        
        subprocess.run([
            "ffmpeg", "-loop", "1", "-i", slide_path, "-c:v", "libx264", "-t", str(slide_duration),
            "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080", video_file_name
        ])
        video_segments.append(video_file_name)
    
    file_list_path = os.path.join(temp_dir, "file_list.txt")
    with open(file_list_path, "w") as file_list:
        for segment in video_segments:
            file_list.write(f"file '{segment}'\n")
    
    subprocess.run([
        "ffmpeg", "-f", "concat", "-safe", "0", "-i", file_list_path, "-i", os.path.join(temp_dir, "all_announcements.mp3"),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-strict", "experimental", "-shortest", output_file
    ])
    
    os.remove(file_list_path)
    print(f"Video created: {output_file}")