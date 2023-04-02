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

# Screen
FPS = 30
RESTART_INTERVAL = 30

# Camera
MOVIE_PATH = "galitime/ressources/movie.mjpg"
CAMERA_LOGFILE = "galitime/logs/camera.log"
START_BYTES = b"\xFF\xD8\xFF"
STOP_BYTES = b"\xFF\xD9"

# Event manager
SAVE_FILE = "event.json"

# Emails manager
INFO_FILE = "email.json"

# Printer settings
PRINTER = "DP-QW410"
PRINT_TIME = 100 # tenths of seconds