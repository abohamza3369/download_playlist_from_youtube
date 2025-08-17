import flet as ft
import yt_dlp
import os
import threading
from pathlib import Path
import re


class YouTubeDownloader:
    def __init__(self):
        self.download_progress = 0
        self.is_downloading = False
        self.current_video = ""

    def progress_hook(self, d, progress_callback=None):
        if d['status'] == 'downloading':
            if 'total_bytes' in d:
                percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                self.download_progress = percent
                filename = d.get('filename', 'Unknown')
                self.current_video = os.path.basename(filename)
                if progress_callback:
                    progress_callback(percent, self.current_video)
        elif d['status'] == 'finished':
            self.download_progress = 100
            if progress_callback:
                progress_callback(100, "Download completed!")

# to can download the best quality for video you must install ffmpeg on amc
# brew install ffmpeg
    def download_video(self, url, output_path, quality, progress_callback=None, completion_callback=None):
        try:
            self.is_downloading = True

            # Configure yt-dlp options
            if quality == "1080p":
                format_selector = "bestvideo[height<=?1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?1080]+bestaudio/best[height<=?1080]"
            elif quality == "720p":
                format_selector = "bestvideo[height<=?720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=?720]+bestaudio/best[height<=?720]"
            elif quality == "480p":
                format_selector = "best[height<=?480]"
            else:  # Audio only
                format_selector = "best audio/best"

            ydl_opts = {
                'format': format_selector,
                'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
                'progress_hooks': [lambda d: self.progress_hook(d, progress_callback)],
                'noplaylist': 'playlist' not in url.lower(),
            }

            # If it's audio only, add audio extraction options
            if quality == "Audio Only":
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            if completion_callback:
                completion_callback(True, "Download completed successfully!")

        except Exception as e:
            if completion_callback:
                completion_callback(False, f"Error: {str(e)}")
        finally:
            self.is_downloading = False


def main(page: ft.Page):
    page.title = "YouTube Video Downloader"
    page.window_width = 700
    page.window_height = 600
    page.window_resizable = True
    page.theme_mode = ft.ThemeMode.LIGHT

# create an object from Class to use the functions
    downloader = YouTubeDownloader()

    # UI Components
    url_input = ft.TextField(
        label="YouTube URL (Video or Playlist)",
        hint_text="Paste your YouTube URL here...",
        expand=True,
        border_radius=10,
    )

    output_path = ft.TextField(
        label="Download Folder",
        value=str(Path.home() / "Downloads/YouTube_Video_Downloader"),
        expand=True,
        border_radius=10,
    )

    quality_dropdown = ft.Dropdown(
        label="Quality",
        value="720p",
        options=[
            ft.dropdown.Option("1080p"),
            ft.dropdown.Option("720p"),
            ft.dropdown.Option("480p"),
            ft.dropdown.Option("Audio Only"),
        ],
        width=150,
    )

    progress_bar = ft.ProgressBar(
        width=400,
        color="blue",
        bgcolor="#eeeeee",
        visible=False,
    )

    progress_text = ft.Text(
        "Ready to download",
        size=14,
        color="grey",
    )

    download_btn = ft.ElevatedButton(
        text="Download",
        icon = ft.CupertinoIcons.DOWNLOAD_CIRCLE,
        #icon=ft.icons.DOWNLOAD,
        color="white",
        bgcolor="blue",
        width=150,
        height=40,
    )



    info_text = ft.Text(
        "",
        size=12,
        color="green",
        text_align=ft.TextAlign.CENTER,
    )

    # def on_dialog_result(e: ft.FilePickerResultEvent):
    #     if e.path:
    #         output_path.value = e.path
    #         output_path.update()
    #
    # file_picker = ft.FilePicker(on_result=on_dialog_result)
    # page.overlay.append(file_picker)
    #
    # def browse_folder(e):
    #     file_picker.get_directory_path("Select Download Folder")
    # _____________________________
    # the function that we use to pick the folder ro download the video on it
    # Create dialog for folder selection

    # directory_picker = ft.FilePicker()
    # page.overlay.append(directory_picker)
    # page.update()
    #
    # # Store selected path
    # selected_path = ft.Text()

    # def pick_folder(e):
    #     # Open folder picker dialog
    #     directory_picker.get_directory_path(
    #         dialog_title="Select Download Folder",
    #         initial_directory="/"  # Optional: set initial directory
    #     )
    #
    # def handle_folder_selected(e: ft.FilePickerResultEvent):
    #     if e.path:
    #         selected_path.value = e.path
    #         page.update()
    #         # Now use e.path as your download directory
    #         print("Selected folder:", e.path)
    #     else:
    #         print("Folder selection cancelled")
    #
    # # Link event handler to folder selection
    # directory_picker.on_result = handle_folder_selected
# #_______________________________________
#     # the button that pick the folder
#     browse_btn = ft.ElevatedButton(
#         text="Browse",
#         icon=ft.CupertinoIcons.FOLDER_OPEN,
#         on_click=pick_folder,
#         width=100,
#         height=40,
#     )

        #_____________________________________________________

    def validate_youtube_url(url):
        youtube_patterns = [
            r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
            r'(?:https?://)?youtu\.be/[\w-]+',
            r'(?:https?://)?(?:www\.)?youtube\.com/(?:embed|v)/[\w-]+',
        ]
        return any(re.match(pattern, url) for pattern in youtube_patterns)

    def update_progress(percent, current_file):
        progress_bar.value = percent / 100
        progress_text.value = f"Downloading: {current_file} ({percent:.1f}%)"
        progress_bar.update()
        progress_text.update()

    def on_download_complete(success, message):
        download_btn.disabled = False
        download_btn.text = "Download"
        download_btn.update()

        progress_bar.visible = False
        progress_bar.update()

        if success:
            info_text.value = message
            info_text.color = "green"
            progress_text.value = "Download completed successfully!"
        else:
            info_text.value = message
            info_text.color = "red"
            progress_text.value = "Download failed!"

        info_text.update()
        progress_text.update()

    def start_download(e):
        url = url_input.value.strip()
        output_folder = output_path.value.strip()

        # Validation
        if not url:
            info_text.value = "Please enter a YouTube URL"
            info_text.color = "red"
            info_text.update()
            return

        if not validate_youtube_url(url):
            info_text.value = "Please enter a valid YouTube URL"
            info_text.color = "red"
            info_text.update()
            return


        try:
            os.makedirs(output_folder, exist_ok=True)
            # Verify the folder was created/exists and is writable
            if not os.path.exists(output_folder):
                info_text.value = "Could not create download folder"
                info_text.color = "red"
                info_text.update()
                return

            # Test write permissions
            test_file = os.path.join(output_folder, "test_write_permission.tmp")
            try:
                with open(test_file, 'w') as f:
                    f.write("test")
                os.remove(test_file)
            except (PermissionError, OSError):
                info_text.value = "No write permission to download folder"
                info_text.color = "red"
                info_text.update()
                return

        except (PermissionError, OSError) as e:
            info_text.value = f"Cannot create folder: {str(e)}"
            info_text.color = "red"
            info_text.update()
            return

        # Start download
        download_btn.disabled = True
        download_btn.text = "Downloading..."
        download_btn.update()

        progress_bar.visible = True
        progress_bar.value = 0
        progress_bar.update()

        info_text.value = ""
        info_text.update()

        progress_text.value = "Starting download..."
        progress_text.update()

        # Run download in separate thread
        def download_thread():
            downloader.download_video(
                url,
                output_folder,
                quality_dropdown.value,
                progress_callback=update_progress,
                completion_callback=on_download_complete
            )

        threading.Thread(target=download_thread, daemon=True).start()

    download_btn.on_click = start_download

    # Layout
    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text(
                    "YouTube Video Downloader",
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    color="blue",
                ),
                ft.Divider(height=20, color="transparent"),

                # URL Input Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("YouTube URL:", size=16, weight=ft.FontWeight.BOLD),
                        url_input,
                    ]),
                    padding=ft.padding.all(10),
                    border=ft.border.all(1, "lightgrey"),
                    border_radius=10,
                ),

                # Settings Section
                ft.Container(
                    content=ft.Column([
                        ft.Text("Download Settings:", size=16, weight=ft.FontWeight.BOLD),
                        ft.Row([
                            output_path,

                        ], spacing=10),
                        ft.Row([
                            quality_dropdown,
                        ], alignment=ft.MainAxisAlignment.START),
                    ]),
                    padding=ft.padding.all(10),
                    border=ft.border.all(1, "lightgrey"),
                    border_radius=10,
                ),

                # Download Section
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            download_btn,
                        ], alignment=ft.MainAxisAlignment.CENTER),
                        ft.Divider(height=10, color="transparent"),
                        progress_bar,
                        progress_text,
                        info_text,
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.all(10),
                ),



            ], spacing=15),
            padding=ft.padding.all(20),
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
