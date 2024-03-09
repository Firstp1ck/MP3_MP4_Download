import os
import tkinter as tk
from tkinter import filedialog, messagebox
from pytube import YouTube
from moviepy.editor import *

def download_video_as_mp3(url, save_path):
    try:
        yt = YouTube(url)
        video = yt.streams.filter(only_audio=True).first()
        out_file = video.download(output_path=save_path)

        # Converting to MP3
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        video_clip = AudioFileClip(out_file)
        video_clip.write_audiofile(new_file)
        
        # Remove the original download
        os.remove(out_file)
        
        messagebox.showinfo("Success", f"Downloaded and converted video to MP3 successfully: {os.path.basename(new_file)}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

def start_download():
    url = url_entry.get()
    folder = folder_path.get()
    if not url.strip() or not folder.strip():
        messagebox.showwarning("Warning", "Please enter a YouTube URL and select a download folder.")
        return
    download_video_as_mp3(url, folder)

app = tk.Tk()
app.title("YouTube to MP3 Downloader")
app.geometry("500x150")

url_label = tk.Label(app, text="YouTube URL:")
url_label.pack()
url_entry = tk.Entry(app, width=50)
url_entry.pack()

folder_path = tk.StringVar()
folder_label = tk.Label(app, text="Download Folder:")
folder_label.pack()
folder_entry = tk.Entry(app, textvariable=folder_path, width=50)
folder_entry.pack()
browse_button = tk.Button(app, text="Browse", command=browse_folder)
browse_button.pack()

download_button = tk.Button(app, text="Download MP3", command=start_download)
download_button.pack()

app.mainloop()
