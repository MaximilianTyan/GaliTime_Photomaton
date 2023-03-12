#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Control window module, contains widget declarative functions, 
functionnality functions are stored in controlfunctions.py
"""

import logging

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt

from screenwindow import ScreenWindow
from controlPages import startpage, optionspage, controlpage, camerapage
from eventmanager import EventManager

logger = logging.getLogger(__name__)
logger.propagate = True


class ControlWindow(QMainWindow):
    """ControlWindow : Main control window holding buttons, labels and every control widget"""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("GaliTime")
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self._shortcutSetup()

        EventManager.setParentWindow(self)

        self.loadPage("start")
        self.show()

    @classmethod
    def getWindow(cls) -> QMainWindow:
        """
        getWindow : Returns the control window instance

        Returns:
            QMainWindow: Control window instance
        """
        return cls

    def loadPage(self, page: str) -> None:
        """
        loadPage : Loads and displays the requested page

        Args:
            page (str): page name
        """
        pagesDict = {
            "start": startpage.StartPage,
            "options": optionspage.OptionsPage,
            "control": controlpage.ControlPage,
            "camera": camerapage.CameraPage,
        }
        self.currentPage = object.__new__(pagesDict[page])
        self.currentPage.__init__(self)
        self.setCentralWidget(self.currentPage.load())

    def _shortcutSetup(self):
        self.FullScreenShortCut = QShortcut("F11", self)
        self.FullScreenShortCut.activated.connect(self.toggleFullscreen)

    def toggleFullscreen(self):
        """
        toggleFullscreen : Toggles fullscreen/windowed view
        """
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, event) -> None:
        """
        closeEvent : Closes the screen window when the control window is closed
        This function is called by QMainWindow close event and shouldn't be called directly

        Args:
            event (Qt Event): Close event
        """
        ScreenWindow.getScreen().close()
        event.accept()
