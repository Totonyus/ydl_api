import logging, params, youtube_dl
from urllib.parse import urlparse, unquote
from fastapi import BackgroundTasks, FastAPI, Response

app = FastAPI()

# used to define if the url is a video, un playlist or a video in a playlist
def define_properties(url):
    properties = {"playlist" : False, "video" : False} # set at the beginning in case params.playlist_detection is empty

    for entry in params.playlist_detection:
        properties = {"playlist" : False, "video" : False} # reset evety loop

        for indicator in entry['video_indicators']:
            properties['video'] = True if url.find(indicator) != -1 else properties['video']

        for indicator in entry['playlist_indicators']:
            properties['playlist'] = True if url.find(indicator) != -1 else properties['playlist']

    return properties

def must_be_checked(url, no_playlist = params.no_playlist):
    properties = define_properties(url)
    is_a_playlist = properties['playlist']
    is_a_video = properties['video']

    # To avoid failing a test for ONE video impossible to download in the entire playlist
    if is_a_video and ((not is_a_playlist) or (is_a_playlist and no_playlist)) :
        return True
    elif is_a_playlist and ((not is_a_video) or (is_a_video and not no_playlist)):
        return False
    else: #In other cases : checking
        return True

### Verify if youtube-dl can find video and the format is right
def check_download(url, format):
    ydl_opts = { # the option ignoreerrors breaks the function but it can be a problem while downloading playlists with unavailable videos inside
        'quiet': True,
        'simulate': True,
        'format': format,
        'noplaylist': params.no_playlist
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            if must_be_checked(url):
                logging.info("Checking download")
                ydl.download([url])
                return {'checked' : True, 'errors' : False}
            else:
                logging.warning("Unable to check download")
                return {'checked' : False, 'errors' : False}
        except:
            return {'checked' : True, 'errors' : True}

### Launch the download instruction
def launch_download(url, ydl_opts):
    logging.info(f"Downloading '{url}' with quality '{ydl_opts['format']}' in '{ydl_opts['outtmpl']}'")

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

@app.get("/download")
async def create_download(response : Response, background_tasks : BackgroundTasks, url: str,
                          format: str = params.default_format, subtitles : str = params.default_subtitles_languages, location: str = "default"):
    decoded_url = unquote(url)
    decoded_format = unquote(format)
    decoded_subtitles = subtitles.split(',') if subtitles is not None else None

    # used to pass useful vars for naming purpose
    ydl_api_opts = {
        'url': decoded_url,
        'hostname' : urlparse(decoded_url).hostname,
        'location_identifier' : location
    }

    download_dir = params.download_dir(ydl_api_opts)

    ydl_opts = {
        'quiet': True,
        'ignoreerrors' : True,
        'outtmpl': download_dir + params.file_name_template(ydl_api_opts),
        'format': decoded_format,
        'noplaylist': params.no_playlist,
        'writesubtitles': subtitles is not None,
        'subtitleslangs' : decoded_subtitles,
        'subtitlesformat': params.default_subtitles_format
    }

    checked_download = check_download(url, decoded_format)

    if checked_download['checked'] is False:
        # background_tasks.add_task(launch_download, decoded_url, ydl_opts)
        response.status_code = 202
    elif checked_download['checked'] and checked_download['errors'] is False:
        # background_tasks.add_task(launch_download, decoded_url, ydl_opts)
        response.status_code = 200
    else:
        logging.error(f"Impossible to download '{decoded_url}'")
        response.status_code = 400

    return {'url' : decoded_url, 'format': decoded_format, 'download_dir' : download_dir, 'status' : response.status_code, 'subtitles' : decoded_subtitles, 'checked_download' : checked_download}
