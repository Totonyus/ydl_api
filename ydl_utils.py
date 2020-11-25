import logging, params, youtube_dl, re
from urllib.parse import urlparse, unquote
import hooks, functools

"""
    Check if all requested presets are available
    if no preset is available, use the 'default' preset (only once)
"""
def existing_presets(preset_identifiers):
    correct_presets = []
    for preset_identifier in preset_identifiers:
        preset_object = params.presets_templates.get(preset_identifier)
        if preset_object is not None:
            correct_presets.append(preset_object)

    if len(correct_presets) == 0: # charge default preset if no preset was found
        correct_presets.append(params.presets_templates.get('default'))

    return correct_presets

"""
    Verify if the url can be checked (playlists shouldn't be checked)
    no_playlist param is for unit testing purpose 
"""
def can_be_checked(url, no_playlist = params.no_playlist):
    url_properties = define_url_properties(url)
    is_a_playlist = url_properties['playlist']
    is_a_video = url_properties['video']

    if is_a_playlist and ((not is_a_video) or (is_a_video and not no_playlist)):
        return False
    else: #In other cases : checking
        return True

"""
    Used to define if the url is a video, un playlist or a video in a playlist
"""
def define_url_properties(url):
    properties = {'playlist' : False, 'video' : False} # set at the beginning in case params.playlist_detection is empty

    for entry in params.playlist_detection:
        properties = {'playlist' : False, 'video' : False} # reset every loop

        for indicator in entry['video_indicators']:
            if url.find(indicator) != -1 : properties['video'] = True

        for indicator in entry['playlist_indicators']:
            if url.find(indicator) != -1 : properties['playlist'] = True

    return properties

"""
    Get definitive parameters to use
    Priority : query_params > preset_params > default_params
"""
def get_definitive_params(query_params, user, preset_params=None):
    default_params = params.presets_templates.get('default')

    if preset_params is None: preset_params = default_params

    definitive_params = {}
    definitive_params['user_name'] = user.get('name') if user is not None else None
    definitive_params['user_token'] = user.get('token') if user is not None else None

    for param in ['format', 'subtitles', 'location', 'filename']:
        definitive_params[param] = query_params.get(param) if query_params.get(param) is not None else preset_params.get(param) if preset_params.get(param) is not None else default_params.get(param)
    return definitive_params

"""
    Check if all downloads successfully passed the checking process
"""
def recap_all_downloads_validity(download_list):
    checked_downloads_number = 0
    download_errors_number = 0

    for download in download_list:
        if download.get('check_result').get('checked') : checked_downloads_number += 1
        if download.get('check_result').get('errors') : download_errors_number += 1
    return {'checked' : checked_downloads_number, 'errors' : download_errors_number, 'total' : len(download_list)}

"""
    Generate download options set 
"""
def set_ydl_opts(url, definitive_params):
    ydl_api_opts = { #used to pass resolve tags in templates
        'hostname' : urlparse(url).hostname,
        'user_name' : definitive_params.get('user_name'),
        'user_token' : definitive_params.get('user_token'),
        'location_identifier' : definitive_params.get('location'),
        'filename_identifier' : definitive_params.get('filename'),
    }

    download_directory_template = params.download_directory_templates.get(ydl_api_opts.get('location_identifier'))
    if download_directory_template is None : download_directory_template = params.download_directory_templates.get('default')
    file_name_template = params.file_name_templates.get(ydl_api_opts.get('filename_identifier'))
    if file_name_template is None: file_name_template = params.file_name_templates.get('default')

    ydl_opts = {
        'quiet': True,
        'ignoreerrors' : True,
        'subtitlesformat': params.default_subtitles_format,
        'noplaylist': params.no_playlist,
        'format': definitive_params.get('format'),
        'subtitleslangs' : definitive_params.get('subtitles').split(',') if definitive_params.get('subtitles') is not None else None,
        'writesubtitles' : definitive_params.get('subtitles') is not None,
        'outtmpl' : resolve_templates_tags(download_directory_template + file_name_template, ydl_api_opts),
        'updatetime' : params.keep_modification_time,
        'progress_hooks' : [functools.partial(hooks.handler, ydl_api_opts)]
    }

    return ydl_opts

"""
    Verify if youtube-dl can find video and the format is right
"""
def check_download_validity(url, download_format):
    ydl_opts = { # the option ignoreerrors breaks the function but it can be a problem while downloading playlists with unavailable videos inside
        'quiet': True,
        'simulate': True,
        'format': download_format,
        'noplaylist': params.no_playlist
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            if can_be_checked(url):
                ydl.download([url])
                return {'checked' : True, 'errors' : False}
            else:
                logging.warning('Unable to check download')
                return {'checked' : False, 'errors' : False} # can't be wrong if not tested right ?
        except:
            return {'checked' : True, 'errors' : True}

"""
    Launch the download instruction
"""
def launch_downloads(url, download_options_sets):
    for option_set in download_options_sets:
        ydl_opts = option_set.get('ydl_opts')
        logging.info(f'Downloading \'{url}\' with quality \'{ydl_opts["format"]}\' in \'{ydl_opts["outtmpl"]}\'')

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

"""
    Resolve tags in templates
"""
def resolve_templates_tags(template_with_tags, ydl_api_opts):
    regex = r'%(\w*)%'

    matches = re.finditer(regex, template_with_tags)

    resolved_path = template_with_tags
    for match in matches:
        tag_value = ydl_api_opts.get(match.group(1))
        if tag_value is not None :
            resolved_path = resolved_path.replace(match.group(0), ydl_api_opts.get(match.group(1)))
        else:
            resolved_path = resolved_path.replace(match.group(0), 'NA')
    return resolved_path

"""
    Generate ydl_opts for all downloads
"""
def generate_ydl_options_sets(url, preset_objects, query_params, user):
    checked_downloads_list = []
    if len(preset_objects) == 0:
        definitive_params = get_definitive_params(query_params, user, None)
        ydl_opts = set_ydl_opts(url, definitive_params)
        checked_downloads_list.append({'check_result' : check_download_validity(url, definitive_params.get('format')), 'ydl_opts' : ydl_opts})
    else:
        for selected_preset in preset_objects:
            definitive_params = get_definitive_params(query_params, user, selected_preset)
            ydl_opts = set_ydl_opts(url, definitive_params)
            checked_downloads_list.append({'check_result' : check_download_validity(url, definitive_params.get('format')), 'ydl_opts' : ydl_opts})
    return checked_downloads_list

"""
    Find the user associated to the given token 
"""
def find_associated_user(token):
    if token is None:
        return None

    for user in params.authorized_users_list:
        if user.get('token') == token:
            return user
    return None
