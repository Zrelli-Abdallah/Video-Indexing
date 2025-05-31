from ultralytics import YOLO
import cv2, os, csv, torch
import torch.nn as nn
import numpy as np
import torchvision.models as models
import torchvision.transforms as transforms
from PIL import Image

# Directories
video_dir = "videos"
keyframes_dir = "keyframes"  # Expected: one folder per video named as title
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

fps = 30  # Adjust if needed

# Load models
seg_model = YOLO("yolov8s-seg.pt")
resnet = models.resnet50(pretrained=True)
resnet.eval()
feature_extractor = torch.nn.Sequential(*(list(resnet.children())[:-1]))

dense_model = nn.Sequential(
    nn.Linear(2048, 1024),
    nn.ReLU(),
    nn.Dropout(0.5),
    nn.Linear(1024, 512),
    nn.ReLU()
)
dense_model.eval()

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

confidence_threshold = 0.5

# Loop through videos
for video_file in os.listdir(video_dir):
    if not video_file.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        continue

    title = os.path.splitext(video_file)[0]
    keyframe_subdir = os.path.join(keyframes_dir, title)
    output_csv = os.path.join(output_dir, f"video_index_{title}.csv")

    if not os.path.isdir(keyframe_subdir):
        print(f"Skipping {title} – no keyframes folder")
        continue

    with open(output_csv, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=[
            "frame_index", "timestamp", "object", "confidence",
            "x_min", "y_min", "x_max", "y_max", "refined_feature_embedding"
        ])
        writer.writeheader()

        for frame_file in sorted(os.listdir(keyframe_subdir)):
            frame_path = os.path.join(keyframe_subdir, frame_file)
            frame_index = int(frame_file.split("_")[1].split(".")[0])
            timestamp = frame_index / fps

            results = seg_model(frame_path)
            pil_image = Image.open(frame_path).convert("RGB")

            for result in results:
                if not result.masks:
                    continue
                for mask, box in zip(result.masks.data, result.boxes):
                    x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                    conf = round(float(box.conf[0]), 2)
                    if conf < confidence_threshold:
                        continue
                    cls = result.names[int(box.cls[0])]

                    cropped = pil_image.crop((x_min, y_min, x_max, y_max))
                    input_tensor = transform(cropped).unsqueeze(0)
                    with torch.no_grad():
                        features = feature_extractor(input_tensor)
                        features = features.view(1, -1)
                        refined_features = dense_model(features)
                    refined_features = refined_features.view(-1).tolist()

                    writer.writerow({
                        "frame_index": frame_index,
                        "timestamp": round(timestamp, 2),
                        "object": cls,
                        "confidence": conf,
                        "x_min": x_min,
                        "y_min": y_min,
                        "x_max": x_max,
                        "y_max": y_max,
                        "refined_feature_embedding": str(refined_features)
                    })

    print(f"Saved object metadata to {output_csv}")

