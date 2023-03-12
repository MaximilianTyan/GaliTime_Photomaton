#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module defining cross file constants
"""

# General
ENCODING = "utf-8"
DATEFORMAT = "yyyy-MM-dd"
LOGGERFORMAT = "%(asctime)s [%(levelname)s] (%(module)s) %(lineno)d : %(message)s"

# Screen
FPS = 30
RESTART_INTERVAL = 30

# Camera
MOVIEPATH = "movie.mjpg"
STARTBYTES = b"\xFF\xD8\xFF"
STOPBYTES = b"\xFF\xD9"

# Event manager
SAVEFILE = "event.json"

# Emails manager
INFOFILE = "email.json"
