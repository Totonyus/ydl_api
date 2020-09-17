import logging, ydl_utils
from urllib.parse import urlparse, unquote
from fastapi import BackgroundTasks, FastAPI, Response

app = FastAPI()

@app.get("/download")
async def create_download(response : Response, background_tasks : BackgroundTasks, url: str,
                          format: str = None, subtitles : str = None, location: str = None, filename : str = None, presets: str = None):

    selected_presets_objects = []
    decoded_presets = []

    if presets is not None:
        decoded_presets = presets.split(',') if presets is not None else None
        selected_presets_objects = ydl_utils.existing_presets(decoded_presets)

    decoded_url = unquote(url)

    query_params = {
        'format' : unquote(format) if format is not None else None,
        'subtitles' : unquote(subtitles) if subtitles is not None else None,
        'location' : unquote(location) if location is not None else None,
        'filename' : unquote(filename) if filename is not None else None,
        'presets' : unquote(presets) if presets is not None else None
    }

    checked_downloads_list = ydl_utils.generate_ydl_opts(selected_presets_objects, query_params, decoded_url)


    validity_check = ydl_utils.are_all_downloads_valid(checked_downloads_list)

    if validity_check.get('checked') == validity_check.get('total') and validity_check.get('errors') == 0:
        background_tasks.add_task(ydl_utils.launch_downloads, decoded_url, checked_downloads_list)
        response.status_code = 200
    elif validity_check.get('checked') != validity_check.get('total'):
        background_tasks.add_task(ydl_utils.launch_downloads, decoded_url, checked_downloads_list)
        response.status_code = 202
    else:
        logging.error(f"Impossible to download '{decoded_url}'")
        response.status_code = 400

    return {'url' : decoded_url, 'presets_errors' : (len(decoded_presets) - len(selected_presets_objects)), 'list' : checked_downloads_list}
