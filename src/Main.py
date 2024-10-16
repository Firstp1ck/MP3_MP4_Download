import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import threading
import time
import requests  # Used for network error handling
from pytube import YouTube, exceptions
from moviepy.editor import AudioFileClip
import logging

# Configuration path using config.ini file (Make sure to set appropriate paths/filenames)
from configparser import ConfigParser
config = ConfigParser()
config.read('config.ini')

# Setting up logging through config ini
logging.basicConfig(level=logging.INFO, filename=config.get('Paths', 'log_file'), filemode='w',
                    format='%(name)s - %(levelname)s - %(message)s')


def validate_url(url: str) -> bool:
    """Validates the URL to ensure it is a valid YouTube URL."""
    regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/watch\?v=[\w-]{11}')
    return re.match(regex, url) is not None


def threaded_download(func):
    """Decorator to run download in a separate thread to keep GUI responsive."""
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()
    return wrapper


@threaded_download
def download() -> None:
    """Handles the operation of downloading the media and applying retries."""
    url = url_entry.get()
    folder = folder_path.get()
    
    if not url or not folder:
        messagebox.showwarning("Warning", "Please enter a valid YouTube URL and select a download folder.")
        return
    
    if not validate_url(url):
        messagebox.showwarning("Invalid URL", "Please enter a valid YouTube URL.")
        return

    # Attempt download with retries for robustness
    try:
        yt = YouTube(url, on_complete_callback=download_complete_callback)
        
        if download_option.get() == 'MP3':
            perform_audio_download_with_retry(yt, folder)
        else:
            perform_video_download_with_retry(yt, folder)
    
    except exceptions.PytubeError as pytube_error:
        logging.error(f"pytube error occurred: {pytube_error}")
        messagebox.showerror("Download Error", f"Failed due to a pytube issue: {str(pytube_error)}")

    except requests.exceptions.RequestException as conn_error:
        logging.error(f"Connection/network error while downloading: {conn_error}")
        messagebox.showerror("Network Error", f"Please check your internet connection: {str(conn_error)}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        logging.error(f"Failed to download/convert: {e}")


def perform_audio_download_with_retry(yt: YouTube, folder: str, retries: int = 3, backoff: int = 2) -> None:
    """Attempt audio download with retries in case of transient failures."""
    for attempt in range(retries):
        try:
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream:
                out_file = audio_stream.download(output_path=folder)
                convert_to_mp3(out_file, folder)
                break  # Exit after successful download
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} of {retries} failed: {str(e)}")
            if attempt + 1 < retries:
                time.sleep(backoff)
            else:
                messagebox.showerror("Error", f"Audio download failed after {retries} attempts: {str(e)}")


def convert_to_mp3(out_file: str, folder: str) -> None:
    """Converts downloaded file to MP3 and removes the original file."""
    base, ext = os.path.splitext(out_file)
    new_file = f"{base}.mp3"
    
    try:
        video_clip = AudioFileClip(out_file)
        video_clip.write_audiofile(new_file)
        os.remove(out_file)  # Clean-up original file

        messagebox.showinfo("Success", f"Downloaded and converted to MP3: {os.path.basename(new_file)}")
        logging.info(f"Converted to MP3: {new_file}")
    except Exception as e:
        messagebox.showerror("Conversion Error", f"Failed to convert to MP3: {str(e)}")
        logging.error(f"MP3 conversion failed: {str(e)}")


def perform_video_download_with_retry(yt: YouTube, folder: str, retries: int = 3, backoff: int = 2) -> None:
    """Attempt video download with retries in case of transient failures."""
    for attempt in range(retries):
        try:
            res = resolution.get()
            itag = None
            if res == '720p':
                itag = yt.streams.filter(res="720p", file_extension='mp4', progressive=True).first().itag
            elif res == '480p':
                itag = yt.streams.filter(res="480p", file_extension='mp4', progressive=True).first().itag
            
            if itag:
                video_stream = yt.streams.get_by_itag(itag)
                video_stream.download(output_path=folder)
                messagebox.showinfo("Success", f"Downloaded video: {os.path.basename(video_stream.default_filename)}")
                logging.info(f"Downloaded video: {video_stream.default_filename}")
                break
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} of {retries} failed: {str(e)}")
            if attempt + 1 < retries:
                time.sleep(backoff)
            else:
                messagebox.showerror("Error", f"Video download failed after {retries} attempts: {str(e)}")


def download_complete_callback(stream, file_path):
    """Callback function after a successful download."""
    logging.info(f"Download complete for {file_path}")


def on_option_change(*args) -> None:
    """Disables resolution selection when MP3 download option is selected."""
    if download_option.get() == 'MP3':
        resolution_combobox.configure(state='disabled')
    else:
        resolution_combobox.configure(state='readonly')


def create_gui_components(master: tk.Tk) -> None:
    """Create all GUI components and arrange them in the main window."""
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


# Initialize app
app = tk.Tk()
app.title("YouTube Downloader")
app.geometry("600x300")

# Global state variables
download_option = tk.StringVar(value='MP3')
folder_path = tk.StringVar()
resolution = tk.StringVar(value='720p')

# Build the GUI
create_gui_components(app)
app.mainloop()