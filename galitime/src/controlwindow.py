#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Control window module, contains widget declarative functions, 
functionnality functions are stored in controlfunctions.py
"""

import logging
from typing import Type, TypeVar

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QShortcut

from .abstractcontrolwindow import AbstractControlWindow
from .controlpages.abstractpage import AbstractPage
from .controlpages.camerapage import CameraPage
from .controlpages.controlpage import ControlPage
from .controlpages.emailpage import MailPage
from .controlpages.optionspage import OptionsPage
from .controlpages.pagesenum import PageEnum
from .controlpages.printerpage import PrinterPage
from .controlpages.startpage import StartPage
from .managers.eventmanager import EventManager
from .screenwindow import ScreenWindow

# ---------- LOGGER SETUP ----------
logger = logging.getLogger(__name__)
logger.propagate = True
# ----------------------------------

ImplementsAbstractPage = TypeVar('ImplementsAbstractPage', bound=AbstractPage)

PAGE_DICT: dict[PageEnum, Type[ImplementsAbstractPage]] = {
    PageEnum.START: StartPage,
    PageEnum.CONTROL: ControlPage,
    PageEnum.CAMERA: CameraPage,
    PageEnum.PRINTER: PrinterPage,
    PageEnum.MAIL: MailPage,
    PageEnum.OPTIONS: OptionsPage
}


class ControlWindow(AbstractControlWindow):
    """ControlWindow : Main control window holding buttons, labels and every control
    widget"""

    def __init__(self) -> None:
        super().__init__()

        self.currentPage = None
        self.setWindowTitle("GaliTime")
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self._shortcutSetup()

        EventManager.setParentWindow(self)

        self.loadPage(PageEnum.START)
        self.show()

    @classmethod
    def getWindow(cls) -> QMainWindow:
        """
        getWindow : Returns the control window instance

        Returns:
            QMainWindow: Control window instance
        """
        return cls

    def loadPage(self, page: PageEnum, *args, **kwargs) -> None:
        """
        loadPage : Loads and displays the requested page

        Args:
            page (str): page name
        """

        self.currentPage = PAGE_DICT[page](self, *args, **kwargs)
        self.setCentralWidget(self.currentPage.load())

    def _shortcutSetup(self):
        self.FullScreenShortCut = QShortcut("F11", self)
        self.FullScreenShortCut.activated.connect(self.toggleFullscreen)

    def toggleFullscreen(self):
        """
        toggleFullscreen : Toggles fullscreen/windowed view
        """
        if self.isFullScreen():
            logger.debug("Toggling Fullscreen OFF")
            self.showNormal()
        else:
            logger.debug("Toggling Fullscreen ON")
            self.showFullScreen()

    def closeEvent(self, event) -> None:
        """
        closeEvent : Closes the screen window when the control window is closed
        This function is called by QMainWindow close event and shouldn't be called
        directly

        Args:
            event (Qt Event): Close event
        """
        logger.info("Control window closed, closing screen window")
        ScreenWindow.getScreen().close()
        event.accept()
