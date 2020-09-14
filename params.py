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
def file_name_template(ydl_api_opts):
    return "%(title)s_(%(height)s).%(ext)s"

# Multiple choices with the parameter &location
def download_dir(ydl_api_opts):
    locations={ ###- --%--- REPLACE ---%--- here with your different download directorues
        'default' : f"{ydl_api_opts.get('hostname')}/",
        #'date' : f"{date.today().strftime('%Y_%m_%d')}/" # for example : &location=date
    }

    if locations.get(ydl_api_opts.get('location_identifier')) is not None:
        location = locations.get(ydl_api_opts.get('location_identifier'))
    else:
        logging.warning(f"{ydl_api_opts.get('location_identifier')} identifier not found. Using the default one instead")
        location = locations.get('default')

    return location
