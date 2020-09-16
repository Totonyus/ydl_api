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
def launch_downloads(url, downloads):
    for download in downloads:
        ydl_opts = download.get('ydl_opts')
        logging.info(f"Downloading '{url}' with quality '{ydl_opts['format']}' in '{ydl_opts['outtmpl']}'")

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

# preset parameters are overide by query params
def set_ydl_opts(definitive_params, url):
    # used to pass useful vars for naming purpose
    ydl_api_opts = {
        'hostname' : urlparse(url).hostname,
        'location_identifier' : definitive_params.get('location'),
        'filename_identifier' : definitive_params.get('filename'),
    }

    logging.error(ydl_api_opts)

    download_dir = params.download_dir(ydl_api_opts)
    name_template = params.file_name_template(ydl_api_opts)

    ydl_opts = {
        'quiet': True,
        'ignoreerrors' : True,
        'subtitlesformat': params.default_subtitles_format,
        'noplaylist': params.no_playlist,
        'format': definitive_params.get('format'),
        'subtitleslangs' : definitive_params.get('subtitles').split(',') if definitive_params.get('subtitles') is not None else None,
        'writesubtitles' : definitive_params.get('subtitles') is not None,
        'outtmpl' : download_dir.get('result') + name_template.get('result'),
        'ydl_api_technical' : {'download_dir_default' : download_dir.get('default'), 'name_template_default' : name_template.get('default')}
    }

    return ydl_opts

def get_definitive_params(query_params, preset = None):
    default_preset = params.get_presets_params('default').get('result')

    if preset is None:
        preset = default_preset

    definitive_params = {}
    for param in ['format', 'subtitles', 'location', 'filename']:
        definitive_params[param] = query_params.get(param) if query_params.get(param) is not None else preset.get(param) if preset.get(param) is not None else default_preset.get(param)
    return definitive_params

@app.get("/download")
async def create_download(response : Response, background_tasks : BackgroundTasks, url: str,
                          format: str = None, subtitles : str = None, location: str = None, filename : str = None, presets: str = None):

    selected_presets_objects = []
    decoded_presets = []

    if presets is not None:
        decoded_presets = presets.split(',') if presets is not None else None
        selected_presets_objects = existing_presets(decoded_presets)

    decoded_url = unquote(url)

    query_params = {
        'format' : unquote(format) if format is not None else None,
        'subtitles' : unquote(subtitles) if subtitles is not None else None,
        'location' : unquote(location) if location is not None else None,
        'filnema' : unquote(filename) if filename is not None else None,
        'presets' : unquote(presets) if presets is not None else None
    }

    checked_downloads_list = []

    if len(selected_presets_objects) == 0:
        definitive_params = get_definitive_params(query_params, None)
        ydl_opts = set_ydl_opts(definitive_params, decoded_url)
        checked_downloads_list.append({'check_result' : check_download(url, definitive_params.get('format')), 'ydl_opts' : ydl_opts})
    else:
        for selected_preset in selected_presets_objects:
            definitive_params = get_definitive_params(query_params, selected_preset)
            ydl_opts = set_ydl_opts(definitive_params, decoded_url)
            checked_downloads_list.append({'check_result' : check_download(url, definitive_params.get('format')), 'ydl_opts' : ydl_opts})

    validity_check = are_all_downloads_valid(checked_downloads_list)

    if validity_check.get('checked') == validity_check.get('total') and validity_check.get('errors') == 0:
        background_tasks.add_task(launch_downloads, decoded_url, checked_downloads_list)
        response.status_code = 200
    elif validity_check.get('checked') != validity_check.get('total'):
        background_tasks.add_task(launch_downloads, decoded_url, checked_downloads_list)
        response.status_code = 202
    else:
        logging.error(f"Impossible to download '{decoded_url}'")
        response.status_code = 400

    return {'url' : decoded_url, 'presets_errors' : (len(decoded_presets) - len(selected_presets_objects)), 'list' : checked_downloads_list}

def are_all_downloads_valid(download_list):
    checked_number = 0
    errors_number = 0

    for download in download_list:
        if download.get('check_result').get('checked') : checked_number += 1
        if download.get('check_result').get('errors') : errors_number += 1
    return {'checked' : checked_number, 'errors' : errors_number, 'total' : len(download_list)}

def existing_presets(presets):
    existing = []
    for preset in presets:
        preset_object = params.get_presets_params(preset)
        if preset_object is not None and preset_object.get('default') is False:
            existing.append(preset_object.get('result'))

    if len(existing) == 0:
        existing.append(params.get_presets_params('default'))

    return existing

#TODO refactoring
#TODO update doc
