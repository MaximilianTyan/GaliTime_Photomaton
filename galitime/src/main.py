#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Main module, creates and links objects and launche windows, apps
"""

import sys

from PyQt5.QtWidgets import QApplication

from .controlwindow import ControlWindow
from .screenwindow import ScreenWindow
from .camera import CameraWrapper
from .printer import ImagePrinter

from . import logger


def main():
    """
    Main function launchgin the photomaton app
    """
    # Main app creation ------------------------------

    logger.setup()

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


if __name__ == "__main__":
    main()
