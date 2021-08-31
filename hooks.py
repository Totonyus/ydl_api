import logging

"""
You can customize this method as you want
    ydl_api_opts = {
        'hostname' : urlparse(url).hostname,
        'user_name' : definitive_params.get('user_name'),
        'user_token' : definitive_params.get('user_token'),
        'location_identifier' : definitive_params.get('location'),
        'filename_identifier' : definitive_params.get('filename'),
        'url' : url,
        'is_playlist' : url_properties.get('playlist'),
        'is_video' : url_properties.get('video')
    }

    download is the standard youtube-dl object
"""
def handler(ydl_opts, download):
    if download.get('status') == 'finished':
        logging.info(f'{download.get("filename")} download finished ({download.get("_total_bytes_str")})')
    if download.get('status') == 'error':
        logging.error(f'Download failed')
