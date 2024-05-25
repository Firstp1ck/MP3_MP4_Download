import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pytube import YouTube
from moviepy.editor import AudioFileClip
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')

def download() -> None:
    """Handles the download operation based on user input."""
    url = url_entry.get()
    folder = folder_path.get()
    if not url or not folder:
        messagebox.showwarning("Warning", "Please enter a YouTube URL and select a download folder.")
        return
    
    try:
        yt = YouTube(url)
        if download_option.get() == 'MP3':
            video = yt.streams.filter(only_audio=True).first()
            if video:
                out_file = video.download(output_path=folder)
                convert_to_mp3(out_file, folder)
            else:
                messagebox.showinfo("Info", "No audio streams available.")
        else:
            download_video(yt, folder)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
        logging.error(f"Failed to download or convert: {e}")

def convert_to_mp3(out_file: str, folder: str) -> None:
    """Converts the downloaded file to MP3 and cleans up the original file."""
    base, ext = os.path.splitext(out_file)
    new_file = f"{base}.mp3"
    video_clip = AudioFileClip(out_file)
    video_clip.write_audiofile(new_file)
    os.remove(out_file)  # Remove the original download
    messagebox.showinfo("Success", f"Downloaded and converted to MP3: {os.path.basename(new_file)}")
    logging.info(f"Converted to MP3: {new_file}")

def download_video(yt: YouTube, folder: str) -> None:
    """Downloads the video at the selected resolution."""
    itag = None
    if resolution.get() == '720p':
        itag = yt.streams.filter(res="720p", file_extension='mp4', progressive=True).first().itag
    elif resolution.get() == '480p':
        itag = yt.streams.filter(res="480p", file_extension='mp4', progressive=True).first().itag
    
    if itag:
        video = yt.streams.get_by_itag(itag)
        video.download(output_path=folder)
        messagebox.showinfo("Success", f"Downloaded video: {os.path.basename(video.default_filename)}")
        logging.info(f"Downloaded video: {video.default_filename}")
    else:
        messagebox.showinfo("Info", "Selected resolution not available. No file was downloaded.")

def on_option_change(*args) -> None:
    """Disables the resolution option when downloading MP3s."""
    if download_option.get() == 'MP3':
        resolution_combobox.configure(state='disabled')
    else:
        resolution_combobox.configure(state='readonly')

def create_gui_components(master: tk.Tk) -> None:
    """Creates and places all GUI components in the master window."""
    url_frame = tk.Frame(master)
    url_frame.pack(pady=10)

    tk.Label(url_frame, text="Insert URL:").pack(side=tk.LEFT)
    global url_entry
    url_entry = tk.Entry(url_frame, width=50)
    url_entry.pack(side=tk.LEFT)

    tk.Radiobutton(master, text="MP3", variable=download_option, value='MP3', command=on_option_change).pack(anchor='w')
    tk.Radiobutton(master, text="Video", variable=download_option, value='Video', command=on_option_change).pack(anchor='w')

    global resolution_combobox
    resolution_combobox = ttk.Combobox(master, textvariable=resolution, values=['720p', '480p'], state='disabled')
    resolution_combobox.pack(pady=5)

    tk.Button(master, text="Browse Download Folder", command=lambda: folder_path.set(filedialog.askdirectory())).pack(pady=5)
    tk.Label(master, textvariable=folder_path, wraplength=500).pack()

    tk.Button(master, text="Download", command=download).pack(pady=10)

app = tk.Tk()
app.title("YouTube Downloader")
app.geometry("600x300")

download_option = tk.StringVar(value='MP3')
folder_path = tk.StringVar()
resolution = tk.StringVar(value='720p')

# Create and pack GUI components
create_gui_components(app)
app.mainloop()