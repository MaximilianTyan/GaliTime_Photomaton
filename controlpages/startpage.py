#!/bin/env python3
# encoding:utf-8
# coding:utf-8

import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtCore import Qt

import stylesheet
from managers.eventmanager import EventManager

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
        logger.debug("Loading start page")
        # Main layout, vertical, contains Title, Button Layout
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
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
        NewEventButton.setStyleSheet(stylesheet.BigBlueButton)
        NewEventButton.clicked.connect(lambda: self.mainWindow.loadPage("options"))
        MainVLayout.addWidget(NewEventButton)

        # 4. Load event
        LoadEventButton = QPushButton("Charger un événement")
        LoadEventButton.setStyleSheet(stylesheet.BigBlueButton)
        LoadEventButton.clicked.connect(EventManager.loadSaveFolder)
        MainVLayout.addWidget(LoadEventButton)

        logger.debug("Start page loaded")
        return MainContainer
