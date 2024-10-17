#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module to handle the event options page
"""

import logging
import os.path

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QAbstractSpinBox
from PyQt5.QtWidgets import QDateEdit, QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget

from ..abstractcontrolwindow import AbstractControlWindow
from ..controlpages.abstractpage import AbstractPage
from ..controlpages.pagesenum import PageEnum
from ..managers.eventmanager import EventManager
from ..screenwindow import ScreenWindow
from ..utilities.constants import DATE_FORMAT
from ..utilities.stylesheet import cssify

# ---------- LOGGER SETUP ----------
logger = logging.getLogger(__name__)
logger.propagate = True
# ----------------------------------

INPUT_GREEN = "background-color: rgb(150, 250, 150);"
INPUT_RED = "background-color: rgb(250, 150, 150);"


class OptionsPage(AbstractPage):
    """
    StartPage : Handles option page functionnality
    """

    def __init__(self, mainWindow: AbstractControlWindow, createEvent=False):
        self.mainWindow = mainWindow

        self.tempEventInfo = {
            "saveFolder": None, "decorFile": None, "eventName": None, "eventDate": None,
        }

        self.EventInput = None
        self.EventDateInput = None
        self.SaveFolderPathInput = None
        self.DecorFileInput = None
        self.errorLabel = None
        self.ExitButton = None

        self.screenWindow = ScreenWindow.getScreen()
        self.createEvent = createEvent

    def load(self) -> QWidget:
        """
        load : Loads the option page in a QWidget and returns it

        Returns:
            PyQt5.QtWidget: Option page loaded layout
        """
        # Main layout, vertical, contains Title, Button Layout
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
        MainVLayout.setContentsMargins(
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10, )
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1. Label "GaliTime Options"
        TitleLabel = QLabel("GaliTime - Options")
        TitleLabel.setStyleSheet("font-size: 50px")
        TitleLabel.setAlignment(Qt.AlignCenter)
        MainVLayout.addWidget(TitleLabel)

        # 2 Options GridLayout EventName
        OptionsGridLayout = QGridLayout()
        MainVLayout.addLayout(OptionsGridLayout)

        # 2.1 Label
        EventInputLabel = QLabel("Nom de l'événement")
        OptionsGridLayout.addWidget(EventInputLabel, 1, 1)

        # 2.2 Line Edit
        self.EventInput = QLineEdit(EventManager.getEventName())
        self.EventInput.setPlaceholderText("Nom de l'événement")
        self.EventInput.setAlignment(Qt.AlignLeft)
        self.EventInput.textEdited.connect(
            lambda: self.EventInput.setStyleSheet(cssify("white"))
        )
        OptionsGridLayout.addWidget(self.EventInput, 1, 2)

        # 2.3 Validate Button
        ValidateNameButton = QPushButton("Valider")
        ValidateNameButton.clicked.connect(self.changeEventName)
        # ValidateNameButton.setStyleSheet(cssify("Big Flat"))
        OptionsGridLayout.addWidget(ValidateNameButton, 1, 3)

        # 3.1 Date Label
        EventInputLabel = QLabel("Date de l'événement")
        OptionsGridLayout.addWidget(EventInputLabel, 2, 1)

        # 3.2 Date
        self.EventDateInput = QDateEdit(QDate.currentDate())
        self.EventDateInput.setDisplayFormat(DATE_FORMAT)
        self.EventDateInput.setAlignment(Qt.AlignLeft)
        self.EventDateInput.dateTimeChanged.connect(
            lambda *_: self.EventDateInput.setStyleSheet(cssify("white"))
        )
        self.EventDateInput.setButtonSymbols(QAbstractSpinBox.NoButtons)
        OptionsGridLayout.addWidget(self.EventDateInput, 2, 2)

        # 3.3 Date
        ValidateDateButton = QPushButton("Valider")
        ValidateDateButton.clicked.connect(self.changeEventDate)
        # ValidateDateButton.setStyleSheet(cssify("Big Flat"))
        OptionsGridLayout.addWidget(ValidateDateButton, 2, 3)

        # 4.1 Save folder Label
        EventInputLabel = QLabel("Dossier d'enregistrement")
        OptionsGridLayout.addWidget(EventInputLabel, 3, 1)

        # 4.2 Save folder input
        self.SaveFolderPathInput = QLineEdit(EventManager.getEventFolder())
        self.SaveFolderPathInput.setAlignment(Qt.AlignLeft)
        self.SaveFolderPathInput.textEdited.connect(
            lambda: self.SaveFolderPathInput.setStyleSheet(cssify("white"))
        )
        OptionsGridLayout.addWidget(self.SaveFolderPathInput, 3, 2)

        # 4.3 Browe button
        BrowseButton = QPushButton("Parcourir")
        BrowseButton.clicked.connect(self.chooseSaveFolderButtonCall)
        # BrowseButton.setStyleSheet(cssify("Big Flat"))
        OptionsGridLayout.addWidget(BrowseButton, 3, 3)

        # 5.1 Decor Image Label
        EventInputLabel = QLabel("Image de décoration")
        OptionsGridLayout.addWidget(EventInputLabel, 4, 1)

        # 5.2 Decor Image input
        self.DecorFileInput = QLineEdit(str(self.screenWindow.getDecorFile()))
        self.DecorFileInput.setAlignment(Qt.AlignLeft)
        self.DecorFileInput.textEdited.connect(
            lambda: self.DecorFileInput.setStyleSheet(cssify("white"))
        )
        OptionsGridLayout.addWidget(self.DecorFileInput, 4, 2)

        # 5.2 Browe button
        BrowseButton2 = QPushButton("Choisir")
        BrowseButton2.clicked.connect(self.chooseDecorFileButtonCall)
        # BrowseButton2.setStyleSheet(cssify("Big Flat"))
        OptionsGridLayout.addWidget(BrowseButton2, 4, 3)

        # 6 Error Label
        self.errorLabel = QLabel()
        self.errorLabel.setAlignment(Qt.AlignCenter)
        self.errorLabel.setStyleSheet("color: rgb(200, 50, 50);")
        MainVLayout.addWidget(self.errorLabel)

        # 7 Save & Cancel button
        ExitButtonsLayout = QHBoxLayout()
        MainVLayout.addLayout(ExitButtonsLayout)

        # 7.1 Save Button
        SaveButton = QPushButton("Enregistrer")
        SaveButton.setStyleSheet(cssify("Tall Green"))
        SaveButton.clicked.connect(self.controlPageCheck)
        ExitButtonsLayout.addWidget(SaveButton)

        # 7.2 Cancel Button
        CancelButton = QPushButton("Annuler")
        CancelButton.setStyleSheet(cssify("Tall Red"))
        CancelButton.clicked.connect(self.cancelOptions)
        ExitButtonsLayout.addWidget(CancelButton)

        if EventManager.isEventOpened():
            # 7.3 Exit button
            self.ExitButton = QPushButton("Quitter")
            self.ExitButton.clicked.connect(self.exitEvent)
            self.ExitButton.setStyleSheet(cssify("Tall"))
            self.ExitButton.setEnabled(True)
            ExitButtonsLayout.addWidget(self.ExitButton)

        TitleLabel.setFocus()

        self.changeEventName()
        self.changeEventDate()
        self._validateParentFolder(EventManager.getEventFolder())
        self._validateDecorFile(ScreenWindow.getScreen().getDecorFile())

        logger.debug("Options page loaded")
        return MainContainer

    def chooseSaveFolderButtonCall(self) -> None:
        """
        choosesaveFolderPath : Prompts the user with a file dialog to choose
        the save folder where to save the event.
        """
        parentFolderPath = QFileDialog.getExistingDirectory(
            self.mainWindow, caption="Dossier d'enregistrement"
        )
        if len(parentFolderPath) == 0:
            logger.warning("Chosen save folder path is empty")

        saveFolderPath = parentFolderPath.removesuffix('/') + '/' + str(
            self.tempEventInfo["eventName"]
            ) + '/'

        self._validateParentFolder(saveFolderPath)

    def chooseDecorFileButtonCall(self) -> None:
        """
        chooseDecorFile : Prompts the user with a file dialog to choose the
        save folder where to save the event.
        """
        selectedFilename = QFileDialog.getOpenFileName(
            self.mainWindow, caption="Image de décor"
        )[0]
        self._validateDecorFile(selectedFilename)

    def _validateParentFolder(self, saveFolderPath: str) -> None:
        self.SaveFolderPathInput.setText(saveFolderPath)

        logger.debug("Validating save folder path: %s", repr(saveFolderPath))

        if not os.path.exists(os.path.dirname(saveFolderPath)):
            logger.error(
                "Parent folder of event folder doesn't exist: %s",
                repr(os.path.dirname(saveFolderPath))
                )

            self.SaveFolderPathInput.setStyleSheet(INPUT_RED)
            self.tempEventInfo["saveFolder"] = None
            return

        self.SaveFolderPathInput.setStyleSheet(INPUT_GREEN)
        self.tempEventInfo["saveFolder"] = saveFolderPath

    def _validateDecorFile(self, decorFilePath: str) -> None:
        self.DecorFileInput.setText(decorFilePath)

        if not os.path.exists(decorFilePath):
            logger.error("Decor file doesn't exist: %s", decorFilePath)
            self.DecorFileInput.setStyleSheet(INPUT_RED)
            self.tempEventInfo["decorFile"] = None
            return

        self.tempEventInfo["decorFile"] = decorFilePath
        self.DecorFileInput.setStyleSheet(INPUT_GREEN)

    def changeEventName(self) -> None:
        """
        changeEventName : Retrieves the event name from the text input and
        saves it as event name
        """
        if self.EventInput.text().strip() != "":
            self.tempEventInfo["eventName"] = self.EventInput.text()
            self.EventInput.setStyleSheet(INPUT_GREEN)
        else:
            self.tempEventInfo["eventName"] = None
            self.EventInput.setStyleSheet(INPUT_RED)

    def changeEventDate(self) -> None:
        """
        changeEventDate : Retrieves the event name from the text input and
        saves it as event name
        """
        date = self.EventDateInput.date()
        if date.isValid():
            self.tempEventInfo["eventDate"] = date.toString(DATE_FORMAT)
            self.EventDateInput.setStyleSheet(INPUT_GREEN)
        else:
            self.tempEventInfo["eventDate"] = None
            self.EventDateInput.setStyleSheet(INPUT_RED)

    # Page switch

    def controlPageCheck(self) -> None:
        """
        controlPageCheck : Checks if all required information for event loading was
        provided and displays an error message if any is missing
        """

        checkDict = {
            "eventName": "Le nom de l'événement doit être validée",
            "eventDate": "La date de l'événement doit être validée",
            "saveFolder": "Le dossier d'enregistrement doit exister",
            "decorFile": "Le fichier de décoration doit exister",
        }
        for field, errorMsg in checkDict.items():
            if self.tempEventInfo[field] is None:
                self.errorLabel.setText(errorMsg)
                return
        logger.debug(
            "All fields checks passed, overwritting current values with fields values"
        )

        EventManager.setEventName(self.tempEventInfo["eventName"])
        EventManager.setEventDate(self.tempEventInfo["eventDate"])
        EventManager.setEventFolder(self.tempEventInfo["saveFolder"])
        self.screenWindow.setDecorFile(self.tempEventInfo["decorFile"])

        if self.createEvent and not EventManager.isEventOpened():
            EventManager.initSaveFolder(EventManager.getEventFolder())

        if not EventManager.isEventOpened():
            logger.debug("Opened event %s", EventManager.getEventName())
            self.screenWindow.startPreview()
            EventManager.setEventOpened(True)

        EventManager.updateInfoFile()
        self.mainWindow.loadPage(PageEnum.CONTROL)

    def cancelOptions(self) -> None:
        """
        cancelOptions : Return function for the option page, returns either to the
        control page if an event is opened, to start page otherwise
        """
        if EventManager.isEventOpened():
            self.mainWindow.loadPage(PageEnum.CONTROL)
        else:
            self.mainWindow.loadPage(PageEnum.START)

    def exitEvent(self) -> None:
        """
        exitEvent : Stops preview, closes current event and returns to start page
        """

        logger.info("Closing event")
        if self.screenWindow.isPreviewing():
            self.screenWindow.stopPreview()

        EventManager.setEventOpened(False)
        self.mainWindow.loadPage(PageEnum.START)
