#!/bin/env python3
# encoding:utf-8
# coding:utf-8

import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt, QTimer

import stylesheet
from eventmanager import EventManager
from emailmanager import EmailManager

from screenwindow import ScreenWindow
from camera import CameraWrapper
from printer import ImagePrinter

logger = logging.getLogger(__name__)
logger.propagate = True

TEMPFILE = "{}/current.jpeg"


class ControlPage:
    """
    StartPage : Handles control page functionnality
    """

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

        self.PhotoButton = None
        self.currentPhotoFullFilePath = None

        self.tempEventInfo = {
            "saveFolder": None,
            "decorFile": None,
            "eventName": None,
            "eventDate": None,
        }

        self.screenWindow = ScreenWindow.getScreen()
        self.camera = CameraWrapper.getCamera()
        self.printer = ImagePrinter.getPrinter()

        self.timer = QTimer()
        self.timer.timeout.connect(self.tickTimer)

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

        # 3 Take Photo
        self.PhotoButton = QPushButton("Prendre la photo")
        self.PhotoButton.setStyleSheet(stylesheet.BigBlueButton)
        self.PhotoButton.clicked.connect(self.photoButtonCallback)
        MainVLayout.addWidget(self.PhotoButton)

        # 4 Email button
        EmailButton = QPushButton("Envoyer par mail")
        EmailButton.clicked.connect(
            lambda: EmailManager.addPhotoToMail(self.currentPhotoFullFilePath)
        )
        EmailButton.setStyleSheet(stylesheet.BigBlueButton)
        MainVLayout.addWidget(EmailButton)

        # 5 Print button
        PrintButton = QPushButton("Imprimer la photo")
        EmailButton.clicked.connect(self.printImage)
        PrintButton.setStyleSheet(stylesheet.BigBlueButton)
        MainVLayout.addWidget(PrintButton)

        # 6 Option Layout
        OptionHLayout = QHBoxLayout()
        MainVLayout.addLayout(OptionHLayout)

        # 6.1 Options button
        OptionButton = QPushButton("Options")
        OptionButton.clicked.connect(lambda: self.mainWindow.loadPage("options"))
        OptionButton.setStyleSheet(stylesheet.BigButton)
        OptionHLayout.addWidget(OptionButton)

        # 6.2 Camera options button
        CamOptionButton = QPushButton("Camera")
        CamOptionButton.clicked.connect(lambda: self.mainWindow.loadPage("camera"))
        CamOptionButton.setStyleSheet(stylesheet.BigButton)
        OptionHLayout.addWidget(CamOptionButton)

        logger.debug("Control page loaded")
        return MainContainer

    def photoButtonCallback(self) -> None:
        """
        photoButton : Function linked to the photoButton, either starts
        the timer countdown or returns to previewing
        """
        if self.screenWindow.isPreviewing():
            self.PhotoButton.setEnabled(False)
            self.PhotoButton.setStyleSheet(stylesheet.BigDisabledButton)
            self.startCountdown()
        else:
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
            self.PhotoButton.setStyleSheet(stylesheet.BigBlueButton)
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
        parentFolder = EventManager.getEventFolder()

        self.screenWindow.stopPreview()

        rawPhoto = self.camera.takePhoto(parentFolder)
        self.screenWindow.displayImage(rawPhoto)

        EventManager.incrementPhotoNumber()
        self.currentPhotoFullFilePath = self.screenWindow.saveImage(
            parentFolder + TEMPFILE
        )

        return self.currentPhotoFullFilePath

    def printImage(self) -> None:
        """
        printImage : Prints the current photo
        """
        self.printer.printImage(self.currentPhotoFullFilePath)
