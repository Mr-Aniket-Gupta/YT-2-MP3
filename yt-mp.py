import streamlit as st
import yt_dlp
import os
from yt_dlp.utils import DownloadError

st.title("YouTube to MP3 Converter")

url = st.text_input("Enter YouTube Video URL")


def get_ydl_opts(player_clients):
    return {
        "format": "bestaudio/best",
        "outtmpl": "%(title)s.%(ext)s",
        "noplaylist": True,
        "extractor_retries": 5,
        "retries": 10,
        "fragment_retries": 10,
        "skip_unavailable_fragments": True,
        "js_runtimes": {
            "deno": {},
            "node": {},
        },
        "extractor_args": {
            "youtube": {
                "player_client": player_clients,
            }
        },
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }


if st.button("Download MP3"):
    if url:
        with st.spinner("Downloading and converting..."):
            try:
                mp3_file = None
                attempts = [
                    ["tv", "android_sdkless", "web"],
                    ["android_sdkless", "tv"],
                ]

                last_error = None
                for player_clients in attempts:
                    ydl_opts = get_ydl_opts(player_clients)
                    try:
                        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                            info = ydl.extract_info(url, download=True)
                            filename = ydl.prepare_filename(info)
                            mp3_file = os.path.splitext(filename)[0] + ".mp3"
                        break
                    except DownloadError as err:
                        last_error = err
                        if "HTTP Error 403" not in str(err):
                            raise

                if not mp3_file:
                    raise last_error if last_error else RuntimeError("Download failed.")

                st.success("Download Completed!")

                with open(mp3_file, "rb") as f:
                    st.download_button(
                        label="Download MP3 File",
                        data=f,
                        file_name=os.path.basename(mp3_file),
                        mime="audio/mp3"
                    )

            except Exception as e:
                error_text = str(e)
                if "HTTP Error 403" in error_text:
                    st.error(
                        "YouTube blocked this request (HTTP 403). "
                        "Make sure the app has `yt-dlp[default]`, `nodejs`, and `ffmpeg` installed."
                    )
                else:
                    st.error(f"Error: {e}")
    else:
        st.warning("Please enter a valid URL")
