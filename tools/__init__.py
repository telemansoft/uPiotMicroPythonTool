# !/usr/bin/env python
# -*- coding: utf-8 -*-
from .. import requests
from os import path, makedirs
from sublime import version, active_window

from ..tools.boards import get_boards_list
from ..tools.command import run_command
from ..tools.quick_panel import quick_panel

VERSION = (0, 0, 1)
ACTIVE_VIEW = None

global SETTINGS_NAME
SETTINGS_NAME = 'upiot.sublime-settings'


def versionize(raw_version):
    """Semantic Versioning

    Convert the given version in the semantic versioning format

    Arguments:
       raw_version {tuple} -- plugin version in a tuple

    Returns:
       [str] -- Semantic Versioning string
    """
    version = ".".join([str(s) for s in raw_version[:3]])
    if(len(raw_version) > 3):
        version += raw_version[3]
    return version

__all__ = ["get_boards_list",
           "run_command",
           "quick_panel"]


def get_headers():
    """
    headers for urllib request
    """

    user_agent = 'uPIOT/{0} (Sublime-Text/{1})'.format(__version__, version())
    headers = {'User-Agent': user_agent}
    return headers


def download_file(file_url, dst_path, callback=None):
    """download file

    Download and save a file from a given url

    Arguments:
       file_url {str} -- url with the file to download
       dst_path {str} -- where file will be stored
       callback {obj} -- callback to show the progress of the download

    Returns:
        bool -- true if the file was successfully downloaded
    """
    downloaded = 0
    progress_qty = 5  # numbers of symbols to show when it downloading (total)
    headers = get_headers()
    filename = file_url.split('/')[-1]
    dst_path = path.join(dst_path, filename)

    # stop if the file already exits
    if(path.exists(dst_path)):
        return True

    with open(dst_path, 'wb') as file:
        req = requests.get(file_url, stream=True, headers=headers)
        total_length = req.headers.get('content-length')

        # File status
        if(req.status_code != 200):
            return False

        if total_length is None:
            file.write(req.content)
        else:
            for chunk in req.iter_content(1024):
                downloaded += len(chunk)
                file.write(chunk)
                done = int(progress_qty * downloaded / int(total_length))
                percent = int(100 * downloaded) / int(total_length)

                if(callback):
                    current_prog = '■' * done
                    new_prog = '   ' * (progress_qty - done)
                    callback("Downloading Firmware {0:.0f}% [{1}{2}]".format(
                        percent, current_prog, new_prog))
        return True


def make_folder(folder_path):
    """make foler

    Make a folder in the given path

    Arguments:
        folder_path {str} -- folder to make

    Raises:
        exc -- [description]
    """
    if(not path.exists(folder_path)):
        import errno

        try:
            makedirs(folder_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise exc
            pass


def set_status(text):
    if(ACTIVE_VIEW):
        ACTIVE_VIEW.set_status('_upiot_', text)


def clean_status():
    if(ACTIVE_VIEW):
        ACTIVE_VIEW.erase_status('_upiot_')


def show_console():
    options = {'panel': 'console', 'toggle': True}
    active_window().run_command('show_panel', options)


__version__ = versionize(VERSION)
