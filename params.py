api_route = "/download"

default_download_format= "bestvideo+bestaudio/best" #https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#format-selection

default_subtitles_languages = None #example : "en,fr"
default_subtitles_format = "srt"

no_playlist = True  #prevent downloading all the playlist when a video url contains playlist id
playlist_detection = [ #used to detect if the url is a video, a playlist or a video in a playlist
    {'video_indicators': ['/watch?'] , 'playlist_indicators' : ['?list=', '&list=']} #youtube
]

root_download_directory = "."
# https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# you can use those tags : %hostname%, %location_identifier%, %filename_identifier%
download_directory_templates={ # you must keep a 'default' preset
    'default' : f"{root_download_directory}/%hostname%/",
    'audio' : f"{root_download_directory}/audio/"
}

# https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# you can use those tags : %hostname%, %location_identifier%, %filename_identifier%
file_name_templates = { # you must keep a 'default' preset
    'default' : "%(title)s_(%(height)s).%(ext)s",
    'audio' : "%(title)s_(%(vbr)s).%(ext)s",
}

presets_templates={ # you must keep a 'default' preset
    'default' : {'format' : default_download_format, 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'audio': {'format' : 'bestaudio', 'subtitles' : default_subtitles_languages, 'location' : 'audio', 'filename' : 'audio'},
    'best' : {'format' : 'bestvideo+bestaudio/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'fullhd' : {'format' : 'best[height=1080]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'hd' : {'format' : 'best[height=720]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'sd' : {'format' : 'best[height=360]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
}
