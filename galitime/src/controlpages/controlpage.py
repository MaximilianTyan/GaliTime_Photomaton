#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module implementing the control page
"""

import os
import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QLabel, QPushButton, QProgressDialog
from PyQt5.QtCore import Qt, QTimer

from ..managers.eventmanager import EventManager
from ..managers.emailmanager import EmailManager
from ..managers.photomanager import PhotoManager

from ..screenwindow import ScreenWindow

from ..peripherals.camera import CameraWrapper
from ..peripherals.printer import ImagePrinter

from ..utilities.stylesheet import cssify
from ..utilities.constants import DEFAULT_PHOTO, TEMP_PHOTO
from ..utilities.constants import PRINT_TIME

logger = logging.getLogger(__name__)
logger.propagate = True


class ControlPage:
    """
    StartPage : Handles control page functionnality
    """

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

        self.PhotoButton = None
        self.PrintButton = None
        self.PauseButton = None
        self.currentPhotoFullFilePath = os.path.abspath(DEFAULT_PHOTO)

        self.tempEventInfo = {
            "saveFolder": None,
            "decorFile": None,
            "eventName": None,
            "eventDate": None,
        }

        self.screenWindow = ScreenWindow.getScreen()
        self.camera = CameraWrapper.getCamera()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tickTimer)

        self.progressDialog = None
        self.printerTimer = QTimer()
        self.printerTimer.timeout.connect(self.tickPrinterTimer)

    def load(self) -> QWidget:
        """
        load : Loads the control page in a QWidget and returns it

        Returns:
            PyQt5.QtWidget: Control page loaded layout
        """
        logger.debug("Loading control page")
        # Main layout, vertical, contains Everything
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1 Label "GaliTime"
        TitleLabel = QLabel("GaliTime")
        TitleLabel.setAlignment(Qt.AlignCenter)
        TitleLabel.setStyleSheet("font-size: 50px")
        MainVLayout.addWidget(TitleLabel)

        # 2 Label Event
        EventLabel = QLabel(EventManager.getEventName())
        EventLabel.setAlignment(Qt.AlignCenter)
        EventLabel.setStyleSheet("font-size: 30px")
        MainVLayout.addWidget(EventLabel)

        # 3. Button grid layout
        ButtonGridLayout = QGridLayout()
        MainVLayout.addLayout(ButtonGridLayout)

        # 3.1 Take Photo
        self.PhotoButton = QPushButton("Prendre la photo")
        self.PhotoButton.setStyleSheet(cssify("Big Blue"))
        self.PhotoButton.clicked.connect(self.photoButtonCallback)
        ButtonGridLayout.addWidget(self.PhotoButton, 0, 0)

        # 3.2 Email button
        self.PauseButton = QPushButton("Pauser l'aperçu")
        self.PauseButton.clicked.connect(self.togglePause)
        self.PauseButton.setStyleSheet(cssify("Big Red"))
        ButtonGridLayout.addWidget(self.PauseButton, 0, 1)

        # 3.3 Email button
        EmailButton = QPushButton("Envoyer par mail")
        EmailButton.clicked.connect(
            lambda: EmailManager.addPhotoToMailFolder(self.currentPhotoFullFilePath)
        )
        EmailButton.setStyleSheet(cssify("Big Blue"))
        ButtonGridLayout.addWidget(EmailButton, 1, 0)

        # 3.4 Print button
        self.PrintButton = QPushButton("Imprimer la photo")
        self.PrintButton.clicked.connect(self.printImage)
        self.PrintButton.setStyleSheet(cssify("Big Blue"))
        ButtonGridLayout.addWidget(self.PrintButton, 1, 1)

        # 6 Option Layout
        OptionHLayout = QHBoxLayout()
        MainVLayout.addLayout(OptionHLayout)

        # 6.1 Options button
        OptionButton = QPushButton("Options")
        OptionButton.clicked.connect(lambda: self.mainWindow.loadPage("options"))
        OptionButton.setStyleSheet(cssify("Big"))
        OptionHLayout.addWidget(OptionButton)

        # 6.2 Camera options button
        CamOptionButton = QPushButton("Camera")
        CamOptionButton.clicked.connect(lambda: self.mainWindow.loadPage("camera"))
        CamOptionButton.setStyleSheet(cssify("Big"))
        OptionHLayout.addWidget(CamOptionButton)

        logger.debug("Control page loaded")
        return MainContainer

    def togglePause(self) -> None:
        """
        togglePause : Pauses/Resumes the preview process
        """
        if self.screenWindow.isPreviewing():
            self.screenWindow.stopPreview()
            self.PauseButton.setText("Reprendre l'aperçu")
            self.PauseButton.setStyleSheet(cssify("Big Green"))

            self.PhotoButton.setEnabled(False)
            self.PhotoButton.setStyleSheet(cssify("Big Disabled"))

            logger.info("Preview paused")
        else:
            self.screenWindow.startPreview()
            self.PauseButton.setText("Pauser l'aperçu")
            self.PauseButton.setStyleSheet(cssify("Big Red"))

            self.PhotoButton.setEnabled(True)
            self.PhotoButton.setStyleSheet(cssify("Big Blue"))

            logger.info("Preview resumed")


    def photoButtonCallback(self) -> None:
        """
        photoButton : Function linked to the photoButton, either starts
        the timer countdown or returns to previewing
        """
        if self.screenWindow.isPreviewing():
            self.PhotoButton.setEnabled(False)
            self.PhotoButton.setStyleSheet(cssify("Big Disabled"))

            self.PauseButton.setEnabled(False)
            self.PauseButton.setStyleSheet(cssify("Big Disabled"))

            self.startCountdown()
        else:
            self.PauseButton.setEnabled(True)
            self.PauseButton.setStyleSheet(cssify("Big Green"))

            self.PhotoButton.setText("Prendre la photo")
            self.screenWindow.startPreview()

    def startCountdown(self) -> None:
        """
        startCountdown : Starts the photo countdown
        """
        if self.timer.isActive():
            return

        self.timer.countdown = 3
        self.timer.start(1000)
        logger.info("Photo countdown started")

    def tickTimer(self) -> None:
        """
        tickTimer : callback function to tick the photo countdown timer
        """
        if self.timer.countdown < 0:
            self.timer.stop()
            # Timer end
            self.screenWindow.showText("")
            self.takePhoto()

            self.PhotoButton.setEnabled(True)
            self.PhotoButton.setStyleSheet(cssify("Big Blue"))
            self.PhotoButton.setText("Revenir à l'aperçu")

            logger.info("Photo countdown ended")
        elif self.timer.countdown == 0:
            self.screenWindow.showText("SOURIEZ")
        else:
            self.screenWindow.showText(self.timer.countdown)

        self.timer.countdown -= 1

    def takePhoto(self) -> str:
        """
        takePhoto : Takes a photo using the camera library and return the

        Returns:
            str: Full photo file path with name
        """
        photoFolder = PhotoManager().getPhotoFolder()

        self.screenWindow.stopPreview()

        rawPhotoFullPath = self.camera.takePhoto(photoFolder)

        if rawPhotoFullPath is None:
            rawPhotoFullPath = os.path.abspath(DEFAULT_PHOTO)

        self.screenWindow.displayImage(rawPhotoFullPath)

        PhotoManager.incrementPhotoNumber()
        self.currentPhotoFullFilePath = self.screenWindow.exportImage(
            EventManager.getEventFolder() + TEMP_PHOTO
        )

        return self.currentPhotoFullFilePath

    def printImage(self) -> None:
        """
        printImage : Prints the current photo
        """

        logger.info("Printing file %s", self.currentPhotoFullFilePath)

        self.progressDialog = QProgressDialog("Printing photo...", "Close", 0, 100)
        self.progressDialog.canceled.connect(self.stopPrinterTimer)
        # self.progressDialog.setAutoClose(True)

        ImagePrinter.printImage(self.currentPhotoFullFilePath)

        self.startPrintTimer()

    def startPrintTimer(self) -> None:
        """
        startPrintTimer : Displays a progress bar indicating the remaining time for the photo
        """
        logger.info("Printer timer started")
        self.printerTimer.ticksPassed = 0
        self.printerTimer.start(int(PRINT_TIME / 100))

        self.PrintButton.setEnabled(False)
        self.PrintButton.setStyleSheet(cssify("Big Disabled"))

    def tickPrinterTimer(self) -> None:
        """
        tickPrinterTimer : Updates the printer progressbar
        """
        if self.printerTimer.ticksPassed >= 100:
            self.stopPrinterTimer()
            return

        self.printerTimer.ticksPassed += 1
        self.progressDialog.setValue(self.printerTimer.ticksPassed)

    def stopPrinterTimer(self) -> None:
        """
        stopPrinterTimer : Stops timer button and renenables the print button
        """
        self.printerTimer.stop()
        logger.info("Printer timer stopped")

        self.PrintButton.setEnabled(True)
        self.PrintButton.setStyleSheet(cssify("Big Blue"))
