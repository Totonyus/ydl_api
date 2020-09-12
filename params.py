default_format="bestvideo+bestaudio/best"

### Change here the download directory and the file name : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# provided vars
# ydl_api_opts = {
#     'url': url,
#     'hostname' : urlparse(url).hostname
# }

def file_name_template(ydl_api_opts):
    return "%(title)s_(%(height)s).%(ext)s"

def download_dir(ydl_api_opts):
    return f"{ydl_api_opts['hostname']}/"
