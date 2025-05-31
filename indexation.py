import whisper, json, os
from moviepy import VideoFileClip

# Input and output directories
video_dir = "videos"
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Load Whisper
model = whisper.load_model('base.en')

def process_video(video_path):
    print(f"Processing {video_path}...")
    video = VideoFileClip(video_path)

    # Metadata
    title = os.path.splitext(os.path.basename(video_path))[0]
    metadata = {
        "Title": title,
        "Duration": video.duration,
        "Format": video_path.split(".")[-1],
        "Resolution": video.size,
    }

    # Transcription
    transcription = model.transcribe(video_path)

    # Save reverse index
    reverse_index = {
        "Video Path": video_path,
        "Transcription": transcription,
        "Labels": [],  # Placeholder
        "Metadata": metadata,
    }
    out_path = os.path.join(output_dir, f"reverse_index_{title}.json")
    with open(out_path, "w") as f:
        json.dump(reverse_index, f, indent=4)
    print(f"Saved: {out_path}")

# Process all videos in the directory
for filename in os.listdir(video_dir):
    if filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        process_video(os.path.join(video_dir, filename))
