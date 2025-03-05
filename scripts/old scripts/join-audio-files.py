import os
import subprocess
from mutagen.mp3 import MP3

# Print the current working directory
print("Current working directory:", os.getcwd())

# find all of the mp3 files in the audio directory
#audio_directory = 'audio'
audio_directory = '.'

announcement_files = [f for f in os.listdir(audio_directory) if f.endswith(".mp3")]
announcement_files.sort()
print(announcement_files)

# Check and print the duration of each mp3 file
for file in announcement_files:
    file_path = os.path.join(audio_directory, file)
    audio = MP3(file_path)
    duration = audio.info.length  # duration in seconds
    print(f"File: {file}, Duration: {duration} seconds")

# Create a half-second silent audio file
if os.path.exists("silence.mp3"):
    os.remove("silence.mp3")
subprocess.run(["ffmpeg", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono", "-t", "0.5", "silence.mp3"])

# Create a text file listing all the mp3 files to be joined
firstFile = True
with open("file_list.txt", "w") as file_list:
    for file in announcement_files:
        file_list.write(f"file '{os.path.join(audio_directory, file)}'\n")
        if not firstFile:
            file_list.write(f"file '{os.path.join(audio_directory, 'silence.mp3')}'\n")
        firstFile = False


output_file = "all_announcements.mp3"
# delete an existing output file
if os.path.exists(output_file):
    os.remove(output_file)
# Use ffmpeg to concatenate the files listed in the text file
subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", "file_list.txt", "-vf", "apad=pad=0.5", "-c:a", "libmp3lame", output_file])
# Clean up the temporary file list
os.remove("file_list.txt")

print(f"All mp3 files have been joined into {output_file}")