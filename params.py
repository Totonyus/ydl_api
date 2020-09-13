### Change here the default format to use : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#format-selection
default_format="bestvideo+bestaudio/best"

### Example : "en,fr"
default_subtitles_languages = None

### if not possible, it will download any available format
default_subtitles_format = "srt"

hide_format_list_in_logs=True

### Change here the download directory and the file name : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# provided vars
# ydl_api_opts = {'url', 'hostname' }

def file_name_template(ydl_api_opts):
    return "%(title)s_(%(height)s).%(ext)s"

def download_dir(ydl_api_opts):
    return f"{ydl_api_opts['hostname']}/"
