import tkinter as tk
from tkinter import ttk
import json
import os
import csv

# Folder containing reverse index JSON files
output_dir = "output"

# Load all reverse_index_*.json files
def load_all_reverse_indexes():
    reverse_indexes = []
    for filename in os.listdir(output_dir):
        if filename.startswith("reverse_index_") and filename.endswith(".json"):
            path = os.path.join(output_dir, filename)
            with open(path, "r") as f:
                data = json.load(f)
                reverse_indexes.append((filename, data))
    return reverse_indexes

# Search for keyword in transcription, metadata, or labels
def search_videos(keyword, reverse_index_dir="output"):
    results = []
    keyword_lower = keyword.lower()

    for filename in os.listdir(reverse_index_dir):
        if filename.startswith("reverse_index_") and filename.endswith(".json"):
            path = os.path.join(reverse_index_dir, filename)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            video_title = filename.replace("reverse_index_", "").replace(".json", "")
            found = False

            # Search in Metadata
            if "Metadata" in data:
                for field in ["title", "description", "tags"]:
                    value = data["Metadata"].get(field, "")
                    if isinstance(value, list):
                        if any(keyword_lower in item.lower() for item in value):
                            found = True
                    elif keyword_lower in str(value).lower():
                        found = True

            # Search in Transcript
            if not found and "Transcription" in data:
                transcript_text = data["Transcription"].get("text", "")
                if keyword_lower in transcript_text.lower():
                    found = True

            #Search in Detected Objects CSV
            if not found:
                csv_path = os.path.join(reverse_index_dir, f"video_index_{video_title}.csv")
                if os.path.exists(csv_path):
                    with open(csv_path, "r", encoding="utf-8") as csvfile:
                        reader = csv.DictReader(csvfile)
                        for row in reader:
                            if "object" in row and keyword_lower == row["object"].lower():
                                found = True
                                break

            if found:
                results.append(video_title)

    return results

# GUI setup
def run_gui():
    def on_search():
        keyword = entry.get().strip()
        if not keyword:
            result_list.delete(0, tk.END)
            result_list.insert(tk.END, "Please enter a keyword.")
            return

        matches = search_videos(keyword)
        result_list.delete(0, tk.END)
        if matches:
            for title in matches:
                ch = "keyword found in : " + title
                result_list.insert(tk.END, ch)
        else:
            result_list.insert(tk.END, "No matching videos found.")

    root = tk.Tk()
    root.title("Video Search System")
    root.geometry("500x400")

    ttk.Label(root, text="Enter a keyword:").pack(pady=10)
    entry = ttk.Entry(root, width=50)
    entry.pack()

    ttk.Button(root, text="Search", command=on_search).pack(pady=10)

    result_list = tk.Listbox(root, width=60, height=15)
    result_list.pack(pady=10)

    root.mainloop()

# Load data and run GUI
reverse_index_data = load_all_reverse_indexes()
run_gui()
