api_route = '/download'
api_route_info = '/info'

default_download_format= 'bestvideo+bestaudio/best' #https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#format-selection

default_subtitles_languages = None #example : 'en,fr'
default_subtitles_format = 'srt'

keep_modification_time = False #True =  modified date of the file will be the upload date, False = current date

no_playlist = True  #prevent downloading all the playlist when a video url contains playlist id
playlist_detection = [ #used to detect if the url is a video, a playlist or a video in a playlist
    {'video_indicators': ['/watch?'] , 'playlist_indicators' : ['?list=', '&list=', '/user/', '/playlists']} #youtube
]

root_download_directory = 'downloads'
# https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# you can use those tags : %hostname%, %location_identifier%, %filename_identifier%, %user_name%
download_directory_templates={ # you must keep a 'default' preset
    'default' : f'{root_download_directory}/',
    #'dad' : '/home/dad/' # utility example
}

# https://github.com/ytdl-org/youtube-dl/tree/3e4cedf9e8cd3157df2457df7274d0c842421945#output-template
# you can use those tags : %hostname%, %location_identifier%, %filename_identifier%, %user_name%
file_name_templates = { # you must keep a 'default' preset
    'default' : 'videos/%hostname%/%(title)s_(%(height)s).%(ext)s',
    'playlist' : 'videos/%hostname%/playlists/%(playlist)s/%(title)s_(%(height)s).%(ext)s',
    'audio' : 'audio/%(title)s.%(ext)s',
}

presets_templates={ # you must keep a 'default' preset
    'default' : {'format' : default_download_format, 'subtitles' : default_subtitles_languages, 'location' : 'default', 'filename' : 'default'},
    'audio': {'format' : 'bestaudio', 'filename' : 'audio'}, # you can skip parameters you want to remain default
    'best' : {'format' : 'bestvideo+bestaudio/best'},
    'fullhd' : {'format' : 'best[height=1080]/bestvideo[height=1080]+bestaudio/best'},
    'hd' : {'format' : 'best[height=720]/bestvideo[height=720]+bestaudio/best'},
    'sd' : {'format' : 'best[height=360]/bestvideo[height=360]+bestaudio/best'},
    'archiving' : {'filename' : 'playlist'},
}

# enable security in case yu want to open the api to the web
enable_users_management = False

authorized_users_list = [ # ---%--- REPLACE ---%--- your token here
    { 'name' : 'default', 'token' : 'ydl_api_very_secret_token', 'force_location' : None },
    #{ 'name' : 'dad', 'token' : 'dad_super_password', 'force_location' : 'dad' } #for example
]
