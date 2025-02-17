import os
import subprocess
from mutagen.mp3 import MP3
from PIL import Image

# Print the current working directory
print("Current working directory:", os.getcwd())
audio_directory = 'audio'
slides_directory = 'slides'

# find all of the mp3 files in the audio directory
announcement_files = [f for f in os.listdir(audio_directory) if f.endswith(".mp3")]
announcement_files.sort()
print(announcement_files)

# Check and print the duration of each mp3 file
durations = {}
for file in announcement_files:
    if file != "all_announcements.mp3" and file != "silence.mp3":
        file_path = os.path.join(audio_directory, file)
        audio = MP3(file_path)
        duration = audio.info.length  # duration in seconds
        durations[file] = duration
        print(f"File: {file}, Duration: {duration} seconds")

# find all of the png files in the slides directory
slide_files = [f for f in os.listdir(slides_directory) if f.endswith(".png")]
slide_files.sort()
print(slide_files)

# Create a temporary directory to store the images with the correct durations
temp_dir = 'temp_slides'
os.makedirs(temp_dir, exist_ok=True)

# Save each slide with the correct duration
for i, slide_file in enumerate(slide_files):
    slide_path = os.path.join(slides_directory, slide_file)
    slide_image = Image.open(slide_path)
    slide_duration = durations[announcement_files[i]]
    temp_slide_path = os.path.join(temp_dir, f'{i}_slide.png')
    slide_image.save(temp_slide_path)
    # Create a video segment for each slide
    subprocess.run(["ffmpeg", "-loop", "1", "-i", temp_slide_path, "-c:v", "libx264", "-t", str(slide_duration), "-pix_fmt", "yuv420p", "-vf", "scale=1920:1080", os.path.join(temp_dir, f'{i}_slide.mp4')])

# Concatenate all the video segments
with open(os.path.join(temp_dir, "file_list.txt"), "w") as file_list:
    for i in range(len(slide_files)):
        file_list.write(f"file '{i}_slide.mp4'\n")

# Use ffmpeg to combine the video segments and audio into a final video
output_file = "morning_announcements.mp4"
# delete an existing output file
if os.path.exists(output_file):
    os.remove(output_file)
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", os.path.join(temp_dir, "file_list.txt"), "-i", os.path.join(audio_directory, "all_announcements.mp3"), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-strict", "experimental", "-shortest", output_file])

# Clean up the temporary files
import shutil
shutil.rmtree(temp_dir)

print(f"Video created: {output_file}")
