import logging
from datetime import date

### Change here the default format to use : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#format-selection
default_format="bestvideo+bestaudio/best"

### Example : "en,fr", None = don't download subtitles
default_subtitles_languages = None

### if not possible, it will download any available format
default_subtitles_format = "srt"

### equivalent of --no-playlist option : if the playlist is in the url True = download only the current video, False = download the whole playlist
no_playlist = True

### if present in url, the url is a playlist.
playlist_detection = [
    {'video_indicators': ['/watch?'] , 'playlist_indicators' : ['?list=', '&list=']}, #preset for youtube
]

### Change here the download directory and the file name : https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# provided vars
# ydl_api_opts = {'url', 'hostname', 'location_identifier' }
root_dir = "."
def download_dir(ydl_api_opts):
    templates={ ###- --%--- REPLACE ---%--- here with your different download directorues
        'default' : f"{root_dir}/{ydl_api_opts.get('hostname')}/",
        'audio' : f"{root_dir}/audio/",
        #'date' : f"{root_dir}{date.today().strftime('%Y_%m_%d')}/" # for example : &location=date
    }
    return get_value(templates, ydl_api_opts, 'location_identifier')

def file_name_template(ydl_api_opts):
    templates = {
        'default' : "%(title)s_(%(height)s).%(ext)s",
        'audio' : "%(title)s_(%(vbr)s).%(ext)s",
    }
    return get_value(templates, ydl_api_opts, 'filename_identifier')

def get_presets_params(preset_name):
    templates={
        'default' : {'format' : default_format, 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
        'audio': {'format' : 'bestaudio', 'subtitles' : default_subtitles_languages, 'location' : 'audio', 'filename' : 'audio'},
        'best' : {'format' : 'bestvideo+bestaudio/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
        'fullhd' : {'format' : 'best[height=1080]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
        'hd' : {'format' : 'best[height=720]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
        'sd' : {'format' : 'best[height=360]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    }

    return get_value(templates, {'preset' : preset_name}, 'preset')

def get_value(list, ydl_api_opts, entry_name):
    default = False

    if list.get(ydl_api_opts.get(entry_name)) is not None:
        result = list.get(ydl_api_opts.get(entry_name))
    else:
        logging.warning(f"{entry_name} : {ydl_api_opts.get(entry_name)} identifier not found. Using the default one instead")
        result = list.get('default')
        default = True
    return {'result' : result, 'default' : default}
