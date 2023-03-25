#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Screen window, contains screen class and control options
"""

import logging

import os, atexit

from PyQt5.QtWidgets import QMainWindow, QLabel
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt, QTimer

from .camera import CameraWrapper

from .constants import FPS, RESTART_INTERVAL

logger = logging.getLogger(__name__)
logger.propagate = True


class ScreenWindow(QMainWindow):
    """
    ScreenWindow : Windows designed to hold the live screen where images will be displayed.
    """

    ScreenInstance = None

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aperçu")
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        self.cam = CameraWrapper.getCamera()
        self.decorFile = ""

        self.text = ""

        self.defaultImage = QPixmap("galitime/ressources/default_cam_view.png")
        self.decorImage = QPixmap(self.decorFile)
        self.screenImage = QPixmap()

        self.screenPage()
        self.show()

        self._shortcutSetup()
        self._setupPreviewTimers()

        atexit.register(self._cleanUp)

        ScreenWindow.ScreenInstance = self

    @classmethod
    def getScreen(cls) -> QMainWindow:
        """
        getScreen : Returns the current screen window instance

        Returns:
            ScreenWindow: Current screen window
        """
        return cls.ScreenInstance

    def setDecorFile(self, decorFile: str) -> None:
        """
        setDecorFile : Set decor file and update image into memory.

        Args:
            decorFile (str): filepath to image file
        """
        self.decorFile = decorFile
        self.decorImage.load(decorFile)

    def getDecorFile(self) -> str:
        """
        getDecorFile : Returns decor image filepath.

        Returns:
            str: decor image filepath
        """
        return self.decorFile

    def isPreviewing(self) -> bool:
        """
        isPreviewing : return true if the preview process is active, false otherwise

        Returns:
            bool: preview process active
        """
        return self.cam.isPreviewing

    def _setupPreviewTimers(self):
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self._updatePreview)

        self.restartTimer = QTimer()
        self.restartTimer.timeout.connect(self.restartPreview)

    def _shortcutSetup(self):
        self.FullScreenSC = QShortcut("F11", self)
        self.FullScreenSC.activated.connect(self.toggleFullscreen)

    def toggleFullscreen(self) -> None:
        """
        toggleFullscreen : Alternates bewteen fullscreen and normal (window) display.
        """
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def screenPage(self) -> None:
        """
        screenPage : Loads the screen page widgets and sets it as page.
        """
        self.Screen = QLabel("")
        self.Screen.setAlignment(Qt.AlignCenter)
        self.Screen.setMaximumSize(1920, 1080)
        self.Screen.setPixmap(self.defaultImage)

        self.Screen.setScaledContents(True)

        self.setCentralWidget(self.Screen)
        self.reset()

    def showText(self, text: str) -> None:
        """
        showText : Displays text to display on image and displays it.

        Args:
            text (str): Text to display
        """
        self.text = str(text)
        if not self.isPreviewing():
            self.updateScreen()

    def displayImage(self, imagepath: str) -> None:
        """
        displayImage : Loads and displays image from supplied imagepath.

        Args:
            imagepath (str): Path to the image (absolute or relative)
        """
        self.screenImage.load(imagepath)
        if not self.isPreviewing():
            self.updateScreen()

    def exportImage(self, filepath: str) -> str:
        """
        saveImage : Saves the image currently displayed on screen (including decor and text) at the filepath.

        Args:
            filepath (str): Filepath with filename to save the image

        Returns:
            str: Filepath where the image was saved (should correpond to suppied filename)
        """
        if os.path.exists(filepath):
            os.remove(filepath)
        self.screenImage.save(filepath)

        return filepath

    def reset(self) -> None:
        """
        reset : Resets screen to default image and clears text.
        """
        self.Screen.setPixmap(self.defaultImage)
        self.Screen.setText("")
        self.Screen.adjustSize()

    def startPreview(self) -> None:
        """
        startPreview : Starts the preview process, setting it to 30 fps ideally, being limited by the camera throughput.
        A preview restart will occur every 30 seconds to keep the camera output stream file size limited.
        """
        self.reset()

        # Launching capture command
        logger.info("Preview started with %(FPS)u fps")
        self.cam.startPreview()

        self.updateTimer.start(round(1000 / FPS))
        self.restartTimer.start(RESTART_INTERVAL * 1000)

    def _updatePreview(self) -> None:
        """
        _updatePreview : internal update timer callback.
        Updating the screen with last frame available from the camera.
        """
        self.screenImage.loadFromData(self.cam.readPreview())
        self.updateScreen()

    def updateScreen(self) -> None:
        """
        updateScreen : Updates the screen with the base image, in addition to decorfile and text overlayed in that order.
        """
        if self.screenImage.isNull():
            # logger.error("Screen Image is NULL, returning from updateScreen")
            return

        painter = QPainter(self.screenImage)
        font = painter.font()
        font.setPointSize(100)
        painter.setFont(font)

        width, height = self.screenImage.width(), self.screenImage.height()

        painter.drawPixmap(0, 0, width, height, self.decorImage)
        painter.drawText(0, 0, width, height, Qt.AlignCenter, str(self.text))

        self.Screen.setPixmap(self.screenImage)

    def stopPreview(self) -> None:
        """
        stopPreview : Stops the preview process and restores camera connection.
        """
        self.cam.stopPreview()
        self.updateTimer.stop()
        self.restartTimer.stop()

        self.cam.connect()
        self.reset()

    def restartPreview(self) -> None:
        """
        restartPreview : Stops and restarts the preview process, see startPreview and stopPreview for more information.
        """
        logger.info("Restarting Preview")
        self.stopPreview()
        self.startPreview()

    def _cleanUp(self):
        try:
            if self.updateTimer.isActive():
                self.updateTimer.stop()
        finally:
            pass
        try:
            if self.restartTimer.isActive():
                self.updateTimer.stop()
        finally:
            pass
