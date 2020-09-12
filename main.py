import logging, params, youtube_dl
from urllib.parse import urlparse
from fastapi import BackgroundTasks, FastAPI, Response

app = FastAPI()

### Verify if youtube-dl can find video
def check_download(url):
    ydl_opts = {
        'listformats' : True
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

### Launch the download instruction
def launch_download(url, ydl_opts):
    logging.info(f"Downloading '{url}' with quality '{ydl_opts['format']}' in '{ydl_opts['outtmpl']}'")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.get("/download")
async def create_download(response : Response, background_tasks:BackgroundTasks,
                          url: str, format: str = params.default_format):
    # used to pass useful vars for naming purpose
    ydl_api_opts = {
        'url': url,
        'hostname' : urlparse(url).hostname
    }

    ydl_opts = {
        'quiet': True,
        'ignoreerrors' : True,
        'outtmpl': params.download_dir(ydl_api_opts) + params.file_name_template(ydl_api_opts),
        'format': params.default_format
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

    return {'message' : message, 'url' : url, 'format': format, 'download_dir' : params.download_dir(ydl_api_opts), 'status' : response.status_code}
