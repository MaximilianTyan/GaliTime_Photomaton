#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Logger module, initializes python logging
"""

import logging
import os

from .constants import ENCODING, LOGGER_FORMAT


def setup():
    """
    setup : Sets up configuration for the python logging module
    """

    if not os.path.exists("galitime/logs"):
        os.mkdir(
            "galitime/logs",
        )

    logging.basicConfig(format=LOGGER_FORMAT, level=0)

    handler = logging.FileHandler("galitime/logs/galitime.log", "wt", encoding=ENCODING)
    formatter = logging.Formatter(LOGGER_FORMAT)
    handler.setFormatter(formatter)

    rootlogger = logging.getLogger()
    rootlogger.addHandler(handler)
