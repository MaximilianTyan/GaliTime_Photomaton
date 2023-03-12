#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Main module, creates and links objects and launche windows, apps
"""

import sys
import logging

from PyQt5.QtWidgets import QApplication

from controlwindow import ControlWindow
from screenwindow import ScreenWindow
from camera import CameraWrapper
from printer import ImagePrinter

# Format setup ----------------------------------

from constants import ENCODING, LOGGERFORMAT

logging.basicConfig(format=LOGGERFORMAT, level=0)

handler = logging.FileHandler("logs/galitime.log", "wt", encoding=ENCODING)
formatter = logging.Formatter(LOGGERFORMAT)
handler.setFormatter(formatter)

rootlogger = logging.getLogger()
rootlogger.addHandler(handler)

# Main app creation ------------------------------

app = QApplication(sys.argv)

cam = CameraWrapper()
printer = ImagePrinter()
screen = ScreenWindow()
main = ControlWindow()

# App execution -----------------------------------

main.show()
screen.show()

cam.connect()

sys.exit(app.exec())
