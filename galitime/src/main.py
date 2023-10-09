#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Main module, creates and links objects and launche windows, apps
"""

import sys

from PyQt5.QtWidgets import QApplication

from .controlwindow import ControlWindow
from .peripherals.camera import CameraWrapper
from .screenwindow import ScreenWindow
from .utilities import logger


def main():
    """
    Main function launching the photomaton app
    """
    # Main app creation ------------------------------

    logger.setup()

    app = QApplication(sys.argv)

    cam = CameraWrapper()
    screen = ScreenWindow()
    control = ControlWindow()

    # App execution -----------------------------------

    control.show()
    screen.show()

    cam.connect()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
