default_format="bestvideo+bestaudio/best"

default_subtitles_languages = None
default_subtitles_format = "srt"

no_playlist = True
playlist_detection = [
    {'video_indicators': ['/watch?'] , 'playlist_indicators' : ['?list=', '&list=']} #youtube
]

root_dir = "."
directories_templates={ # you must keep a 'default' preset
    'default' : f"{root_dir}/%hostname%/",
    'audio' : f"{root_dir}/audio/"
}

filename_templates = { # you must keep a 'default' preset
    'default' : "%(title)s_(%(height)s).%(ext)s",
    'audio' : "%(title)s_(%(vbr)s).%(ext)s",
}

presets_templates={ # you must keep a 'default' preset
    'default' : {'format' : default_format, 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'audio': {'format' : 'bestaudio', 'subtitles' : default_subtitles_languages, 'location' : 'audio', 'filename' : 'audio'},
    'best' : {'format' : 'bestvideo+bestaudio/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'fullhd' : {'format' : 'best[height=1080]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'hd' : {'format' : 'best[height=720]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'sd' : {'format' : 'best[height=360]/best', 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
}
