import psutil
import re, os
import pathlib
import logging

def get_active_downloads_list():
    children_process = psutil.Process().children(recursive=True)

    active_downloads_list = []
    for child in children_process:
        active_download = {
            'command_line': f'{child.cmdline()}',
            'pid': child.pid
        }

        active_downloads_list.append(active_download)

    return active_downloads_list


def get_current_download_file_destination(cmdline):
    regex = r'\'file:(.*\/)(.*)\''

    match = re.search(regex, f'{cmdline}')

    part_filename = f'{match.group(1)}{match.group(2)}'
    filename = part_filename.rstrip('.part')

    path = match.group(1)
    filename_stem = pathlib.Path(filename).stem
    extension = pathlib.Path(filename).suffix

    return {
        'part_filename': part_filename,
        'filename': filename,
        'path': path,
        'filename_stem': filename_stem,
        'extension': extension,
    }


def is_a_child_process(pid):
    children_process = psutil.Process().children(recursive=True)

    is_child = False

    for child in children_process:
        if child.pid == pid:
            is_child = True

    return is_child

def get_child_object(pid):
    children_process = psutil.Process().children(recursive=True)

    for child in children_process:
        if child.pid == pid:
            return child

    return None

def terminate_active_download(pid):
    child = get_child_object(int(pid))

    if child is not None:
        child.terminate()
        filename_info = get_current_download_file_destination(child.cmdline())

        new_name = f'{filename_info.get("path")}{filename_info.get("filename_stem")}_terminated{filename_info.get("extension")}'

        os.rename(filename_info.get('part_filename'), new_name)


def terminate_all_active_downloads():
    for download in get_active_downloads_list():
        terminate_active_download(download.get('pid'))
