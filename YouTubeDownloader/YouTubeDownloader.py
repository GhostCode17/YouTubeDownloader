from customtkinter import *

import tkinter
import pytube
import requests
import PIL
import io
import os
import threading

class PythonApp(CTk):

    def __init__(self):
        
        super().__init__()

        set_appearance_mode("dark")
        set_default_color_theme("green")

        self.wm_title("YouTube downloader")
        self.wm_resizable(False, False)

        self.youtube_video = None
        
        self.error_message = "An error has occurred\n"
        self.error_message += "\nPossible causes:"
        self.error_message += "\n* Invalid URL"
        self.error_message += "\n* Internet connection"
        self.error_message += "\n* Video not available"
        self.error_message += "\n* Others"

        self.download_complete_message = "Your download is complete!"
        
        pytube.request.default_range_size = 1_048_576

        self.entry_youtube_link = CTkEntry(self, placeholder_text= "YouTube link")
        self.entry_youtube_link.grid(row= 0, column= 0, padx= 5, pady= 5)

        self.label_video_thumbnail = CTkLabel(self, text= "")

        self.label_video_information = CTkLabel(self, text= "")

        self.button_start = CTkButton(self, text= "Start", command= self.process_youtube_link)
        self.button_start.grid(row= 0, column= 1, padx= 5, pady= 5)

        self.combobox_video_format = CTkComboBox(self)

        self.button_download = CTkButton(self, text= "Download", command= self.download_youtube_video)

        self.progressbar_download_progress = CTkProgressBar(self)

    def process_youtube_link(self):

        self.progressbar_download_progress.grid_forget()
        self.progressbar_download_progress.set(0)

        try:

            youtube_video__ = pytube.YouTube(self.entry_youtube_link.get())

            video_thumbnail = CTkImage(light_image= PIL.Image.open(io.BytesIO(requests.get(youtube_video__.thumbnail_url).content)))
            video_thumbnail.configure(size= (170, 95)) 

            video_title = youtube_video__.title

            video_channel = youtube_video__.author

            video_duration = [youtube_video__.length] * 3 # [seconds, minutes, hours]
            video_duration[2] //= 3600
            video_duration[1] -= video_duration[2] * 3600
            video_duration[1] //= 60
            video_duration[0] -= video_duration[2] * 3600 + video_duration[1] * 60
            video_duration = f"{video_duration[2]:02d}:{video_duration[1]:02d}:{video_duration[0]:02d}" if video_duration[2] else f"{video_duration[1]:02d}:{video_duration[0]:02d}"

            video_formats = []

            for index in range(0, len(youtube_video__.streams)):

                stream = youtube_video__.streams[index]

                combobox_item = f"({index + 1})"
                combobox_item += " - "
                combobox_item += stream.mime_type.replace('/', ' - ').capitalize()
                combobox_item += " - "

                if stream.type == "video":
                    
                    combobox_item += stream.resolution
                    combobox_item += " - "
                    combobox_item += "With audio" if stream.is_progressive else "Without audio"
            
                else:
                    combobox_item += stream.abr

                video_formats.append(combobox_item)

            self.label_video_thumbnail.grid(row= 1, column= 0, padx= 5, pady= 5)
            self.label_video_thumbnail.configure(image= video_thumbnail)

            self.label_video_information.grid(row= 2, column= 0, padx= 5, pady= 5)
            self.label_video_information.configure(text= f"* {video_title}\n* Channel: {video_channel}\n* Duration: {video_duration}", justify = LEFT)

            self.combobox_video_format.grid(row= 1, column= 1, padx= 5, pady= 5)
            self.combobox_video_format.configure(values= video_formats)
            self.combobox_video_format.set(video_formats[0])

            self.button_download.grid(row= 2, column= 1, padx= 5, pady= 5)

            # For security------------------------|
            #                                     |
            self.youtube_video = youtube_video__ #|
            #                                     |
            # ------------------------------------|

            self.youtube_video.register_on_complete_callback(self.on_youtube_video_downloaded)
            self.youtube_video.register_on_progress_callback(self.on_youtube_video_downloading)

        except:
            tkinter.messagebox.showerror("Error", self.error_message)

    def download_youtube_video(self):
        
        stream_to_download = self.youtube_video.streams[int(self.combobox_video_format.get().split(" - ")[0].replace("(", "").replace(")", "")) - 1]
        
        file_name, file_extension = os.path.splitext(stream_to_download.default_filename)
        file_name = tkinter.filedialog.asksaveasfilename(confirmoverwrite= True, defaultextension= file_extension, filetypes= [("File", f"*{file_extension}")], initialfile= file_name, title= "YouTube downloader")

        if len(file_name):

            self.progressbar_download_progress.grid(row= 3, column= 1, padx= 5, pady= 5)
            self.progressbar_download_progress.set(0)

            self.button_start.configure(state= DISABLED)
            self.button_download.configure(state= DISABLED)
            
            try:
                threading.Thread(target= lambda stream_to_download, file_name: stream_to_download.download(os.path.dirname(file_name), os.path.basename(file_name)), args= [stream_to_download, file_name]).start()
                
            except:

                tkinter.messagebox.showerror("Error", self.error_message)

                self.button_start.configure(state= NORMAL)
                self.button_download.configure(state= NORMAL)

    def on_youtube_video_downloaded(self, *_):

        tkinter.messagebox.showinfo("YouTube downloader", self.download_complete_message)

        self.button_start.configure(state= NORMAL)
        self.button_download.configure(state= NORMAL)

        self.wm_title("YouTube downloader")

    def on_youtube_video_downloading(self, stream, _, bytes_remaining):

        download_progress = round(1 - bytes_remaining / stream.filesize, 2)

        self.progressbar_download_progress.set(download_progress)
        self.wm_title(f"YouTube downloader - ({int(100 * download_progress)}%)")

if __name__ == "__main__":
    PythonApp().mainloop()