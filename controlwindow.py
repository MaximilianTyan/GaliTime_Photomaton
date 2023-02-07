#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Control window module, contains widget declarative functions, 
functionnality functions are stored in controlfunctions.py
"""

import logging

from PyQt5.QtWidgets import QMainWindow, QWidget
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextEdit,
    QDateEdit,
    QAbstractSpinBox,
)
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt, QDate

from ressources import stylesheet
import controlfunctions as ctrl

logger = logging.getLogger(__name__)
logger.propagate = True

ENCODING = "utf-8"


class ControlWindow(QMainWindow):
    """ControlWindow : Main control window holding buttons, labels and every control widget"""

    def __init__(
        self, screen: object, cam: object, printer: object, argv: list = None
    ) -> None:

        # Parameter check
        if argv is None:
            argv = []

        super().__init__()
        ctrl.init(self, screen, cam, printer)

        self.setWindowTitle("GaliTime")
        self.setWindowFlags(Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)

        startWithPage = argv[1] if len(argv) >= 2 else "startPage"

        if startWithPage == "startPage":
            self.startPage()
        elif startWithPage == "optionsPage":
            self.optionsPage()
        elif startWithPage == "camOptionsPage":
            self.camOptionsPage()
        else:
            self.startPage()

        self.show()
        self.shortcutSetup()

    def shortcutSetup(self):
        self.FullScreenSC = QShortcut("F11", self)
        self.FullScreenSC.activated.connect(self.toggleFullscreen)

    def toggleFullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def closeEvent(self, event) -> None:
        self.screen.close()
        event.accept()

    def startPage(self):
        logger.debug("Loading start page")
        # Main layout, vertical, contains Title, Button Layout
        MainContainer = QWidget(self)
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
        NewEventButton.clicked.connect(self.optionsPage)
        MainVLayout.addWidget(NewEventButton)

        # 4. Load event
        LoadEventButton = QPushButton("Charger un événement")
        LoadEventButton.setStyleSheet(stylesheet.BigBlueButton)
        LoadEventButton.clicked.connect(lambda: ctrl.loadSaveFolder(self))
        MainVLayout.addWidget(LoadEventButton)

        self.setCentralWidget(MainContainer)
        logger.debug("Start page loaded")

    def optionsPage(self):
        logger.debug("Loading options page")
        # Main layout, vertical, contains Title, Button Layout
        MainContainer = QWidget(self)
        MainVLayout = QVBoxLayout()
        MainVLayout.setAlignment(Qt.AlignVCenter)
        MainContainer.setLayout(MainVLayout)

        # 1. Label "GaliTime Options"
        TitleLabel = QLabel("GaliTime - Options")
        TitleLabel.setStyleSheet("font-size: 50px")
        TitleLabel.setAlignment(Qt.AlignCenter)
        MainVLayout.addWidget(TitleLabel)

        # 2 Options GridLayout EventName
        OptionsGridLayout = QGridLayout()
        MainVLayout.addLayout(OptionsGridLayout)

        # 2.1 Line Edit
        self.EventInput = QLineEdit(self.eventName)
        self.EventInput.setPlaceholderText("Nom de l'événement")
        self.EventInput.setAlignment(Qt.AlignCenter)
        OptionsGridLayout.addWidget(self.EventInput, 1, 1)

        # 2.2 Validate Button
        ValidateNameButton = QPushButton("Valider")
        ValidateNameButton.clicked.connect(lambda: ctrl.changeEventName(self))
        ValidateNameButton.setStyleSheet(stylesheet.BigFlatButton)
        OptionsGridLayout.addWidget(ValidateNameButton, 1, 2)

        # 3.1 Date
        self.EventDateInput = QDateEdit(QDate.currentDate())
        self.EventDateInput.setDisplayFormat(ctrl.DATEFORMAT)
        self.EventDateInput.setAlignment(Qt.AlignCenter)
        self.EventDateInput.setButtonSymbols(QAbstractSpinBox.NoButtons)
        OptionsGridLayout.addWidget(self.EventDateInput, 2, 1)

        # 3.2 Date
        ValidateDateButton = QPushButton("Valider")
        ValidateDateButton.clicked.connect(lambda: ctrl.changeEventDate(self))
        ValidateDateButton.setStyleSheet(stylesheet.BigFlatButton)
        OptionsGridLayout.addWidget(ValidateDateButton, 2, 2)

        # 4.1 saveFolderPath label
        self.saveFolderPathLabel = QLabel(
            "Dossier d'enregistrement:\n" + str(self.saveFolder)
        )
        self.saveFolderPathLabel.setAlignment(Qt.AlignCenter)
        self.saveFolderPathLabel.setWordWrap(True)
        OptionsGridLayout.addWidget(self.saveFolderPathLabel, 3, 1)

        # 4.2 Browe button
        BrowseButton = QPushButton("Parcourir")
        BrowseButton.clicked.connect(lambda: ctrl.choosesaveFolderPath(self))
        BrowseButton.setStyleSheet(stylesheet.BigFlatButton)
        OptionsGridLayout.addWidget(BrowseButton, 3, 2)

        # 5.1 Decorfile label
        self.DecorFileLabel = QLabel("Image de Décoration:\n" + self.screen.decorFile)
        self.DecorFileLabel.setAlignment(Qt.AlignCenter)
        self.saveFolderPathLabel.setWordWrap(True)
        OptionsGridLayout.addWidget(self.DecorFileLabel, 4, 1)

        # 5.2 Browe button
        BrowseButton2 = QPushButton("Choisir")
        BrowseButton2.clicked.connect(lambda: ctrl.chooseDecorFile(self))
        BrowseButton2.setStyleSheet(stylesheet.BigFlatButton)
        OptionsGridLayout.addWidget(BrowseButton2, 4, 2)

        # 6 Error Label
        self.errorLabel = QLabel()
        self.errorLabel.setAlignment(Qt.AlignCenter)
        self.errorLabel.setStyleSheet("color: rgb(200,50,50)")
        MainVLayout.addWidget(self.errorLabel)

        # 7 Save & Cancel button
        ExitButtonsLayout = QHBoxLayout()
        MainVLayout.addLayout(ExitButtonsLayout)

        # 7.1 Save Button
        SaveButton = QPushButton("Enregistrer")
        SaveButton.setStyleSheet(stylesheet.BigButton)
        SaveButton.clicked.connect(lambda: ctrl.controlPageCheck(self))
        ExitButtonsLayout.addWidget(SaveButton)

        # 7.1 Cancel Button
        CancelButton = QPushButton("Annuler")
        CancelButton.setStyleSheet(stylesheet.BigRedButton)
        CancelButton.clicked.connect(lambda: ctrl.cancelOptions(self))
        ExitButtonsLayout.addWidget(CancelButton)

        TitleLabel.setFocus()
        self.setCentralWidget(MainContainer)
        logger.debug("Options page loaded")

    def controlPage(self):
        logger.debug("Loading control page")
        # Main layout, vertical, contains Everything
        MainContainer = QWidget(self)
        MainVLayout = QVBoxLayout()
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1 Label "GaliTime"
        TitleLabel = QLabel("GaliTime")
        TitleLabel.setAlignment(Qt.AlignCenter)
        TitleLabel.setStyleSheet("font-size: 50px")
        MainVLayout.addWidget(TitleLabel)

        # 2 Label Event
        EventLabel = QLabel(self.eventName)
        EventLabel.setAlignment(Qt.AlignCenter)
        EventLabel.setStyleSheet("font-size: 30px")
        MainVLayout.addWidget(EventLabel)

        # 3 Take Photo
        self.PhotoButton = QPushButton("Prendre la photo")
        self.PhotoButton.setStyleSheet(stylesheet.BigBlueButton)
        self.PhotoButton.clicked.connect(lambda: ctrl.photoButton(self))
        MainVLayout.addWidget(self.PhotoButton)

        # 4 Email button
        EmailButton = QPushButton("Envoyer par mail")
        EmailButton.clicked.connect(lambda: ctrl.addPhotoToMail(self))
        EmailButton.setStyleSheet(stylesheet.BigBlueButton)
        MainVLayout.addWidget(EmailButton)

        # 5 Print button
        PrintButton = QPushButton("Imprimer la photo")
        EmailButton.clicked.connect(ctrl.printImage)
        PrintButton.setStyleSheet(stylesheet.BigBlueButton)
        MainVLayout.addWidget(PrintButton)

        # 6 Option Layout
        OptionHLayout = QHBoxLayout()
        MainVLayout.addLayout(OptionHLayout)

        # 6.1 Options button
        OptionButton = QPushButton("Options")
        OptionButton.clicked.connect(self.optionsPage)
        OptionButton.setStyleSheet(stylesheet.BigButton)
        OptionHLayout.addWidget(OptionButton)

        # 6.2 Camera options button
        CamOptionButton = QPushButton("Camera")
        CamOptionButton.clicked.connect(self.camOptionsPage)
        CamOptionButton.setStyleSheet(stylesheet.BigButton)
        OptionHLayout.addWidget(CamOptionButton)

        self.setCentralWidget(MainContainer)
        logger.debug("Control page loaded")

    def camOptionsPage(self):
        logger.debug("Loading camera options page")
        MainContainer = QWidget()
        MainVLayout = QVBoxLayout()
        MainContainer.setLayout(MainVLayout)

        # 2 Available cameras Layout
        CamsHLayout = QHBoxLayout()
        MainVLayout.addLayout(CamsHLayout)

        # 2.1 Choice box listing items
        self.CamsChoiceBox = QComboBox()
        ctrl.updateCamList(self)
        CamsHLayout.addWidget(self.CamsChoiceBox)

        # 2.2 Update button
        CamsUpdateButton = QPushButton("MAJ Liste caméra")
        CamsUpdateButton.clicked.connect(lambda: ctrl.updateCamList(self))
        CamsHLayout.addWidget(CamsUpdateButton)

        # 3 Info Grid Layout
        InfoGridLayout = QGridLayout()
        MainVLayout.addLayout(InfoGridLayout)

        # 3.1 Abilities Layout
        AbilitiesVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(AbilitiesVLayout, 0, 0)

        # 3.1.1 Abilities list button
        AbilitiesUpdateButton = QPushButton("MAJ Abilities")
        AbilitiesUpdateButton.clicked.connect(lambda: ctrl.updateAbilities(self))
        AbilitiesVLayout.addWidget(AbilitiesUpdateButton)

        # 3.1.2 Abilities list button
        self.AbilitiesText = QTextEdit()
        AbilitiesVLayout.addWidget(self.AbilitiesText)

        # 3.2 Config Layout
        ConfigVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(ConfigVLayout, 0, 1)

        # 3.2.1 Config list button
        ConfigUpdateButton = QPushButton("MAJ Config")
        ConfigUpdateButton.clicked.connect(lambda: ctrl.updateConfig(self))
        ConfigVLayout.addWidget(ConfigUpdateButton)

        # 3.2.2 Config list button
        self.ConfigText = QTextEdit()
        ConfigVLayout.addWidget(self.ConfigText)

        # 3.3 About Layout
        AboutVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(AboutVLayout, 1, 0)

        # 3.3.1 About list button
        AboutUpdateButton = QPushButton("MAJ About")
        AboutUpdateButton.clicked.connect(lambda: ctrl.updateAbout(self))
        AboutVLayout.addWidget(AboutUpdateButton)

        # 3.3.2 About list button
        self.AboutText = QTextEdit()
        AboutVLayout.addWidget(self.AboutText)

        # 3.4 Summary Layout
        SummaryVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(SummaryVLayout, 1, 1)

        # 3.4.1 Summary list button
        SummaryUpdateButton = QPushButton("MAJ Summary")
        SummaryUpdateButton.clicked.connect(lambda: ctrl.updateSummary(self))
        SummaryVLayout.addWidget(SummaryUpdateButton)

        # 3.4.2 Summary list button
        self.SummaryText = QTextEdit()
        SummaryVLayout.addWidget(self.SummaryText)

        # 4 Reconnect Return layout
        ReconnectReturnLayout = QHBoxLayout()
        MainVLayout.addLayout(ReconnectReturnLayout)

        # 4. Reconnect camera button
        ReconnectButton = QPushButton("Reconnexion caméra")
        ReconnectButton.setStyleSheet(stylesheet.BigDisabledButton)
        ReconnectButton.clicked.connect(lambda: ctrl.reconnectCamera(self))
        ReconnectReturnLayout.addWidget(ReconnectButton)

        # 5 Return button
        ReturnButton = QPushButton("Retour")
        ReturnButton.setStyleSheet(stylesheet.BigRedButton)
        ReturnButton.clicked.connect(self.controlPage)
        ReconnectReturnLayout.addWidget(ReturnButton)

        self.setCentralWidget(MainContainer)
        logger.debug("Camera options page loaded")
