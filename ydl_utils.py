import logging, params, youtube_dl, re
from urllib.parse import urlparse, unquote

"""
    Return the correct template entry_name if exists. If not, return the 'default' template
"""
def get_template_from_list(list, ydl_api_opts, entry_name):
    default = False

    if list.get(ydl_api_opts.get(entry_name)) is not None:
        result = list.get(ydl_api_opts.get(entry_name))
    else:
        logging.warning(f"{entry_name} : {ydl_api_opts.get(entry_name)} identifier not found. Using the default one instead")
        result = list.get('default')
        default = True
    return {'result' : result, 'default' : default}

"""
    Check if all requested presets are available
    if no preset available, use the 'default' preset (only once)
"""
def existing_presets(presets):
    existing = []
    for preset in presets:
        preset_object = get_template_from_list(params.presets_templates, {'preset_identifier' : preset}, 'preset_identifier')
        if preset_object is not None and preset_object.get('default') is False:
            existing.append(preset_object.get('result'))

    if len(existing) == 0:
        existing.append(get_template_from_list(params.presets_templates, {'preset_identifier' : 'default'}, 'preset_identifier'))

    return existing

"""
    Verify if the url can be checked (playlists shouldn't be checked)
    no_playlist param is for unit testing purpose 
"""
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

"""
    Used to define if the url is a video, un playlist or a video in a playlist
"""
def define_properties(url):
    properties = {"playlist" : False, "video" : False} # set at the beginning in case params.playlist_detection is empty

    for entry in params.playlist_detection:
        properties = {"playlist" : False, "video" : False} # reset every loop

        for indicator in entry['video_indicators']:
            properties['video'] = True if url.find(indicator) != -1 else properties['video']

        for indicator in entry['playlist_indicators']:
            properties['playlist'] = True if url.find(indicator) != -1 else properties['playlist']

    return properties

"""
    Get definitive params to use
    Priority : query_params > preset_params > default_params
"""
def get_definitive_params(query_params, preset_params = None):
    default_params = get_template_from_list(params.presets_templates, {'preset_identifier' : 'default'}, 'preset_identifier').get('result')

    if preset_params is None:
        preset_params = default_params

    definitive_params = {}
    for param in ['format', 'subtitles', 'location', 'filename']:
        definitive_params[param] = query_params.get(param) if query_params.get(param) is not None else preset_params.get(param) if preset_params.get(param) is not None else default_params.get(param)
    return definitive_params

"""
    Check if all downloads successfully passed the checking process
"""
def are_all_downloads_valid(download_list):
    checked_number = 0
    errors_number = 0

    for download in download_list:
        if download.get('check_result').get('checked') : checked_number += 1
        if download.get('check_result').get('errors') : errors_number += 1
    return {'checked' : checked_number, 'errors' : errors_number, 'total' : len(download_list)}

"""
    Generate download options 
"""
def set_ydl_opts(definitive_params, url):
    ydl_api_opts = {
        'hostname' : urlparse(url).hostname,
        'location_identifier' : definitive_params.get('location'),
        'filename_identifier' : definitive_params.get('filename'),
    }

    download_dir = get_template_from_list(params.directories_templates, ydl_api_opts, 'location_identifier')
    name_template = get_template_from_list(params.filename_templates, ydl_api_opts, 'filename_identifier')

    ydl_opts = {
        'quiet': True,
        'ignoreerrors' : True,
        'subtitlesformat': params.default_subtitles_format,
        'noplaylist': params.no_playlist,
        'format': definitive_params.get('format'),
        'subtitleslangs' : definitive_params.get('subtitles').split(',') if definitive_params.get('subtitles') is not None else None,
        'writesubtitles' : definitive_params.get('subtitles') is not None,
        'outtmpl' : resolve_parameters(download_dir.get('result') + name_template.get('result'), ydl_api_opts),
        'ydl_api_technical' : {'download_dir_default' : download_dir.get('default'), 'name_template_default' : name_template.get('default')}
    }

    return ydl_opts

"""
    Verify if youtube-dl can find video and the format is right
"""
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

"""
    Launch the download instruction
"""
def launch_downloads(url, downloads):
    for download in downloads:
        ydl_opts = download.get('ydl_opts')
        logging.info(f"Downloading '{url}' with quality '{ydl_opts['format']}' in '{ydl_opts['outtmpl']}'")

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

"""
    Resolve parameters in path
"""
def resolve_parameters(path, ydl_api_opts):
    regex = r"%(\w*)%"

    matches = re.finditer(regex, path)

    resolved_path = path
    for match in matches:
        resolved_path = resolved_path.replace(match.group(0), ydl_api_opts.get(match.group(1)))
    return resolved_path

"""
    Generate ydl_opts for all downloads
"""
def generate_ydl_opts(presets, query_params, decoded_url):
    checked_downloads_list = []
    if len(presets) == 0:
        definitive_params = get_definitive_params(query_params, None)
        ydl_opts = set_ydl_opts(definitive_params, decoded_url)
        checked_downloads_list.append({'check_result' : check_download(decoded_url, definitive_params.get('format')), 'ydl_opts' : ydl_opts})
    else:
        for selected_preset in presets:
            definitive_params = get_definitive_params(query_params, selected_preset)
            ydl_opts = set_ydl_opts(definitive_params, decoded_url)
            checked_downloads_list.append({'check_result' : check_download(decoded_url, definitive_params.get('format')), 'ydl_opts' : ydl_opts})
    return checked_downloads_list
