import logging, ydl_utils, params
from urllib.parse import urlparse, unquote
from fastapi import BackgroundTasks, FastAPI, Response

app = FastAPI()

@app.get(params.api_route)
async def download_request(response : Response, background_tasks : BackgroundTasks, url, token = None,
                          format = None, subtitles  = None, location = None, filename  = None, presets = None):

    decoded_url = unquote(url)
    decoded_presets = [] # from string to list
    selected_presets_objects = [] # store presets objects required by the presets field

    if presets is not None:
        decoded_presets = presets.split(',')
        selected_presets_objects = ydl_utils.existing_presets(decoded_presets)  # transform string in object

    user = None
    if params.enable_users_management:
        user = ydl_utils.find_associated_user(unquote(token))

    if params.enable_users_management and user is None:
        logging.warning(f'An unauthorized user tried to download {decoded_url}')
        response.status_code = 401 # unauthorized
        return {'status_code' : response.status_code}

    query_parameters = { # parameters object build form url query parameters
        'format' : unquote(format) if format is not None else None,
        'subtitles' : unquote(subtitles) if subtitles is not None else None,
        'location' : unquote(location) if location is not None else None,
        'filename' : unquote(filename) if filename is not None else None,
        'presets' : unquote(presets) if presets is not None else None
    }

    # override location setting of the preset for the current user
    if params.enable_users_management and user.get('force_location') is not None :
        query_parameters['location'] = user.get('force_location')

    # generate all options sets for all download
    downloads_options_sets = ydl_utils.generate_ydl_options_sets(decoded_url, selected_presets_objects, query_parameters, user)

    # count the number of check downloads and the number of errors
    validity_check = ydl_utils.recap_all_downloads_validity(downloads_options_sets)

    # if all downloads were checked and without errors, we can ensure the file will be correctly downloaded
    if validity_check.get('checked') == validity_check.get('total') and validity_check.get('errors') == 0:
        background_tasks.add_task(ydl_utils.launch_downloads, decoded_url, downloads_options_sets)
        response.status_code = 200 # request ok
    # if not all downloads were checked, we can't ensure all files will be correctly downloaded
    elif validity_check.get('checked') != validity_check.get('total'):
        background_tasks.add_task(ydl_utils.launch_downloads, decoded_url, downloads_options_sets)
        response.status_code = 202 # request ok but result not granted
    # if all downloads are in error, we can ensure no file will be downloaded
    else:
        logging.error(f'Impossible to download \'{decoded_url}\'')
        response.status_code = 400 # bad request

    return {
        'status_code' : response.status_code,
        'url' : decoded_url,
        'presets_errors' : (len(decoded_presets) - len(selected_presets_objects)),
        'list' : downloads_options_sets
    }
