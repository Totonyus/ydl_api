import logging

"""
You can customize this method as you want
ydl_opts provides 'hostname', 'user_name', 'user_token, 'location_identifier', 'filename_identifier'
download is the standard youtube-dl object
"""
def handler(ydl_opts, download):
    if download.get('status') == 'finished':
        logging.info(f'{download.get("filename")} download finished ({download.get("_total_bytes_str")})')
    if download.get('status') == 'error':
        logging.error(f'Download failed')
