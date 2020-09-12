import logging

from urllib.parse import urlparse
from fastapi import BackgroundTasks, FastAPI, Request, Response

import youtube_dl

app = FastAPI()

### Launch the download instruction
def launch_download(url, ydl_opts):
    logging.info(f"Downloading '{url}' with quality '{ydl_opts['format']}' in '{ydl_opts['outtmpl']}'")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

### Verify if youtube-dl can find video
def check_download(url):
    ydl_opts = {
      'listformats' : True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.get("/download")
async def create_download(request: Request, response : Response, background_tasks:BackgroundTasks):
    url = request.query_params['url']
    hostname = urlparse(url).hostname

    ### Change here the download directory and the file name : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
    download_dir = f"---%--- REPLACE ---%---/{hostname}/"
    filename = "%(title)s_(%(height)s).%(ext)s"

    ### Change here the default format to use : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#format-selection
    try:
      format = request.query_params['format']
    except:
      format = "bestvideo+bestaudio/best"

    ydl_opts = {
        'quiet': True,
        'ignoreerrors' : True,
        'outtmpl': download_dir + filename,
        'format': format
    }

    try:
      check_download(url)
    except:
      message = "Impossible to download"
      logging.error(f"Impossible to download '{url}'")
      response.status_code = 404
    else:
      message = "Download launched"
      background_tasks.add_task(launch_download, url, ydl_opts)
      response.status_code = 200

    return {'message' : message, 'url' : url, 'format': format, 'download_dir' : download_dir}
