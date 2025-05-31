import csv
import os
from PIL import Image
import cv2
import imagehash

# Set directories
video_dir = 'videos'
keyframes_dir = 'keyframes'
output_dir = 'output'
os.makedirs(keyframes_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

# Process each video
for video_file in os.listdir(video_dir):
    if not video_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        continue

    video_path = os.path.join(video_dir, video_file)
    title = os.path.splitext(video_file)[0]
    frame_output_folder = os.path.join(keyframes_dir, title)
    os.makedirs(frame_output_folder, exist_ok=True)
    csv_output_path = os.path.join(output_dir, f'keyframe_index_{title}.csv')

    print(f"Extracting frames from: {video_file}")
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open {video_file}")
        continue

    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_index = 0

    with open(csv_output_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['frame_index', 'timestamp', 'hash'])
        writer.writeheader()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = frame_index / fps
            frame_filename = os.path.join(frame_output_folder, f'frame_{frame_index:04d}.jpg')
            cv2.imwrite(frame_filename, frame)

            try:
                hash_value = str(imagehash.phash(Image.open(frame_filename)))
            except Exception as e:
                hash_value = "error"
                print(f"Error hashing frame {frame_index} of {title}: {e}")

            writer.writerow({
                'frame_index': frame_index,
                'timestamp': round(timestamp, 2),
                'hash': hash_value
            })

            frame_index += 1

    cap.release()
    print(f"Finished extracting for {video_file} → {frame_output_folder}")
