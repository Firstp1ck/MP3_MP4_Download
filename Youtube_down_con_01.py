import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pytube import YouTube
from moviepy.editor import *

def download():
    url = url_entry.get()
    folder = folder_path.get()
    if not url or not folder:
        messagebox.showwarning("Warning", "Please enter a YouTube URL and select a download folder.")
        return
    
    try:
        yt = YouTube(url)
        if download_option.get() == 'MP3':
            video = yt.streams.filter(only_audio=True).first()
            out_file = video.download(output_path=folder)
            base, ext = os.path.splitext(out_file)
            new_file = base + '.mp3'
            video_clip = AudioFileClip(out_file)
            video_clip.write_audiofile(new_file)
            os.remove(out_file)  # Remove the original download
            messagebox.showinfo("Success", f"Downloaded and converted to MP3: {os.path.basename(new_file)}")
        else:
            itag = None
            if resolution.get() == '720p':
                itag = yt.streams.filter(res="720p", file_extension='mp4', progressive=True).first().itag
            elif resolution.get() == '480p':
                itag = yt.streams.filter(res="480p", file_extension='mp4', progressive=True).first().itag
            if itag:
                video = yt.streams.get_by_itag(itag)
                video.download(output_path=folder)
                messagebox.showinfo("Success", f"Downloaded video: {os.path.basename(video.default_filename)}")
            else:
                messagebox.showinfo("Info", "Selected resolution not available. No file was downloaded.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def on_option_change(*args):
    if download_option.get() == 'MP3':
        resolution_combobox.configure(state='disabled')
    else:
        resolution_combobox.configure(state='readonly')

app = tk.Tk()
app.title("YouTube Downloader")
app.geometry("600x300")

download_option = tk.StringVar(value='MP3')

# Create a frame for URL label and entry
url_frame = tk.Frame(app)
url_frame.pack(pady=10)

tk.Label(url_frame, text="Insert URL:").pack(side=tk.LEFT)
url_entry = tk.Entry(url_frame, width=50)
url_entry.pack(side=tk.LEFT)

folder_path = tk.StringVar()
resolution = tk.StringVar(value='720p')

tk.Radiobutton(app, text="MP3", variable=download_option, value='MP3', command=on_option_change).pack(anchor='w')
tk.Radiobutton(app, text="Video", variable=download_option, value='Video', command=on_option_change).pack(anchor='w')

resolution_combobox = ttk.Combobox(app, textvariable=resolution, values=['720p', '480p'], state='disabled')
resolution_combobox.pack(pady=5)

tk.Button(app, text="Browse Download Folder", command=lambda: folder_path.set(filedialog.askdirectory())).pack(pady=5)
tk.Label(app, textvariable=folder_path, wraplength=500).pack()

tk.Button(app, text="Download", command=download).pack(pady=10)

app.mainloop()