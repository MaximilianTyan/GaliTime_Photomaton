#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module defining cross file constants
"""

# General
ENCODING = "utf-8"
DATE_FORMAT = "yyyy-MM-dd"
LOGGER_FORMAT = "%(asctime)s [%(levelname)s] (%(module)s) %(lineno)d : %(message)s"

# Files
LOG_FOLDER = "galitime/logs/"
EVENT_SAVE_FILE = "event.json"
EMAIL_INFO_FILE = "email.json"
TEMP_PHOTO = "last_photo.jpg"

APP_LOG_FILE = LOG_FOLDER + "galitime.log"

# Screen
FPS = 30
RESTART_INTERVAL = 30

# Camera
MOVIE_PATH = "galitime/ressources/movie.mjpg"
CAMERA_LOG_FILE = LOG_FOLDER + "camera.log"
START_BYTES = b"\xFF\xD8\xFF"
STOP_BYTES = b"\xFF\xD9"

# Printer settings
PRINTER = "DP-QW410"
PRINT_TIME = 10e3  # milliseconds

# Defaults files
DEFAULT_CAM_VIEW = "galitime/ressources/default_cam_view.png"
DEFAULT_DECOR = "galitime/ressources/default_decor.png"
DEFAULT_PHOTO = "galitime/ressources/mire.png"
