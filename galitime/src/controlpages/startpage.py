#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module implementing the start page
"""

import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt

from ..managers.eventmanager import EventManager

from ..utilities.stylesheet import cssify

logger = logging.getLogger(__name__)
logger.propagate = True


class StartPage:
    """
    StartPage : Handles start page functionnality
    """

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

    def load(self):
        """
        load : Loads the start page in a QWidget and returns it

        Returns:
            PyQt5.QtWidget: Start page loaded layout
        """
        # Main layout, vertical, contains Title, Button Layout
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
        MainVLayout.setContentsMargins(
            self.mainWindow.width() // 10, 0, self.mainWindow.width() // 10, 0
        )
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1. Label "GaliTime Options"
        TitleLabel = QLabel("GaliTime")
        TitleLabel.setStyleSheet("font-size: 100px")
        TitleLabel.setAlignment(Qt.AlignCenter)
        MainVLayout.addWidget(TitleLabel)

        # 2. Subtitle crédits
        TitleLabel = QLabel("Photomaton by Galileo")
        TitleLabel.setStyleSheet("font-size: 50px")
        TitleLabel.setAlignment(Qt.AlignCenter)
        MainVLayout.addWidget(TitleLabel)

        # 3. New event
        NewEventButton = QPushButton("Nouvel événement")
        NewEventButton.setStyleSheet(cssify("Big Blue"))
        NewEventButton.clicked.connect(self.createEvent)
        MainVLayout.addWidget(NewEventButton)

        # 4. Load event
        LoadEventButton = QPushButton("Charger un événement")
        LoadEventButton.setStyleSheet(cssify("Big Blue"))
        LoadEventButton.clicked.connect(self.openEvent)
        MainVLayout.addWidget(LoadEventButton)

        logger.debug("Start page loaded")
        return MainContainer

    def openEvent(self):
        if EventManager.loadSaveFolder():
            self.mainWindow.loadPage("options")
        else:
            logger.error("Could not load event folder")

    def createEvent(self):
        self.mainWindow.loadPage("options", createEvent=True)
