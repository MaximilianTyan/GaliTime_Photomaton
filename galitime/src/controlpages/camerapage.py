#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module managing the camera options page
"""

import inspect
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QPushButton, QTextEdit, QLabel
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

from ..abstractcontrolwindow import AbstractControlWindow
from ..controlpages.abstractpage import AbstractPage
from ..controlpages.pagesenum import PageEnum
from ..peripherals.camera import CameraWrapper
from ..utilities.stylesheet import cssify

# ---------- LOGGER SETUP ----------
logger = logging.getLogger(__name__)
logger.propagate = True
# ----------------------------------

CHOSEN_STRING = " sélectionnée"


class CameraPage(AbstractPage):
    """
    StartPage : Handles camera page functionality
    """

    def __init__(self, mainWindow: AbstractControlWindow) -> None:
        self.PropertiesText: QTextEdit = None
        self.mainWindow = mainWindow
        self.camera: CameraWrapper = CameraWrapper.getCamera()

        self.ReconnectButton = None

        self.CamsChoiceBox = None
        self.AbilitiesText = None
        self.AbilitiesText = None
        self.ConfigText = None
        self.AboutText = None
        self.SummaryText = None

    def load(self) -> QWidget:
        """
        load : Loads the camera page in a QWidget and returns it

        Returns:
            PyQt5.QtWidget: Camera page loaded layout
        """
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
        MainVLayout.setContentsMargins(
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10, )
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1. Column Layout
        ColumnsVLayout = QHBoxLayout()
        MainVLayout.addLayout(ColumnsVLayout)

        # 1.1 Left Column Layout
        LeftVLayout = QVBoxLayout()
        ColumnsVLayout.addLayout(LeftVLayout)

        # 1.1.1 Choice box listing items
        AbilitiesListLabel = QLabel("Informations sur la caméra")
        AbilitiesListLabel.setAlignment(Qt.AlignHCenter)
        LeftVLayout.addWidget(AbilitiesListLabel)

        # 1.1.2 Abilities list button
        self.PropertiesText = QTextEdit()
        LeftVLayout.addWidget(self.PropertiesText)

        # 1.2 Right Column Layout
        RightVLayout = QVBoxLayout()
        ColumnsVLayout.addLayout(RightVLayout)

        # 1.2.1 Available cameras Layout
        CamsVLayout = QVBoxLayout()
        CamsVLayout.setAlignment(Qt.AlignTop)
        RightVLayout.addLayout(CamsVLayout)

        # 1.2.1.1 Camera listing label
        CamListLabel = QLabel("Caméras disponibles")
        CamListLabel.setAlignment(Qt.AlignHCenter)
        CamsVLayout.addWidget(CamListLabel)

        # 1.2.1.2 Available cameras list layout
        CamsListHLayout = QHBoxLayout()
        CamsVLayout.addLayout(CamsListHLayout)

        # 1.2.1.2.1 Choice box listing items
        self.CamsChoiceBox = QComboBox()
        self.updateCamList()
        CamsListHLayout.addWidget(self.CamsChoiceBox)

        # 1.2.1.2.2 Update button
        CamsUpdateButton = QPushButton("Rafraichir")
        CamsUpdateButton.setStyleSheet("Thin")
        CamsUpdateButton.clicked.connect(self.updateCamList)
        CamsListHLayout.addWidget(CamsUpdateButton)

        # 1.2.2 Control buttons Layout
        ControlButtonsVLayout = QVBoxLayout()
        ControlButtonsVLayout.setAlignment(Qt.AlignBottom)
        RightVLayout.addLayout(ControlButtonsVLayout)

        # 1.2.2.1 Abilities list button
        AbilitiesUpdateButton = QPushButton("Rafraichir")
        AbilitiesUpdateButton.setStyleSheet("Thin")
        AbilitiesUpdateButton.clicked.connect(self.updateAll)
        ControlButtonsVLayout.addWidget(AbilitiesUpdateButton)

        # 1.2.2.2 Reconnect camera button
        self.ReconnectButton = QPushButton("Reconnexion caméra")
        self.ReconnectButton.setStyleSheet(cssify("Tall Disabled"))
        self.ReconnectButton.clicked.connect(self.reconnectCamera)
        ControlButtonsVLayout.addWidget(self.ReconnectButton)
        self.updateReconnectButton()

        # 1.2.2.3 Return button
        ReturnButton = QPushButton("Retour")
        ReturnButton.setStyleSheet(cssify("Tall Red"))
        ReturnButton.clicked.connect(lambda: self.mainWindow.loadPage(PageEnum.CONTROL))
        ControlButtonsVLayout.addWidget(ReturnButton)

        logger.debug("Camera options page loaded")
        return MainContainer

    def reconnectCamera(self) -> None:
        """
        reconnectCamera : Tries to reconnect gphoto2.Camera to the camera
        peripheral and updates the camera status.
        """
        logger.info("Reconnecting camera")
        # self.cam.__init__()
        self.camera.connect()
        self.updateReconnectButton()

    def updateReconnectButton(self) -> None:
        """
        updateReconnectButton : Updates the camera reconnect button style
        according to the camera state. If camera is already connected,
        displays disable button.
        """
        if not self.camera.isConnected():
            self.ReconnectButton.setStyleSheet(cssify("Tall Blue"))
            self.ReconnectButton.setEnabled(True)
        else:
            self.ReconnectButton.setStyleSheet(cssify("Tall Disabled"))
            self.ReconnectButton.setEnabled(False)

    def updateCamList(self) -> None:
        """
        updateCamList : Updates the camera list choice box with all
        available cameras, puts None if no camera is available
        """
        self.CamsChoiceBox.clear()
        camList = self.camera.listCams()

        if len(camList) == 0 or camList is None:
            self.CamsChoiceBox.addItem("None")
            logger.warning("No camera detected")
            return

        logger.debug("Updating camera list with %d entries", len(camList))

        for cam in camList:
            for i in cam:
                self.CamsChoiceBox.addItem(i)

    @staticmethod
    def filteredDir(obj) -> dict:
        """
        filteredDir : Converts a Swig object properties to a dictionnary
        discarding useless functions such as thisown() and executing callable
        objects such as get_children().

        Args:
            obj (Camera data): Data object to be filtered

        Returns:
            dict: Filtered attributes
        """
        outdict = {}

        for attr in dir(obj):
            if attr.startswith("_"):
                continue

            if attr in (
                    "acquire", "append", "disown", "next", "own", "this", "thisown",):
                continue

            if attr.startswith("reserved"):
                continue

            attrValue = object.__getattribute__(obj, attr)
            try:
                textValue = attrValue()
            except TypeError:
                textValue = attrValue
            except Exception as error:
                logger.error("DirFilter ERROR: %s", error)
                logger.error(
                    "Called: %s", inspect.getframeinfo(inspect.currentframe()).function
                )

            if isinstance(textValue, str):
                textValue = '"' + textValue + '"'

            outdict[attr] = textValue

        return outdict

    @staticmethod
    def htmlTablize(datadict: dict) -> str:
        """
        HTMLTablize : Formats the given dictionnary into an HTML table

        Args:
            datadict (dict): Dictionnary to reformat

        Returns:
            str: Raw HTML
        """
        text = '\n'.join(
            [
                "<table>",
                "<tr>",
                "<td> Attribute </td>",
                "<td> Value </td>",
                "</tr>"
            ]
        )

        for key, value in datadict.items():
            text += '\n'.join(
                [
                    "<tr>",
                    f"<td> {key} </td>",
                    f"<td> {value} </td>",
                    "</tr>"
                ]
            )

        text += "</table>"
        text += "<br>"
        return text

    def updateAll(self) -> None:
        """
        updateAll : Updates the camera properties table
        """
        propertiesDict = {
            "Capacités": self.camera.getAbilities(),
            "Configration": self.camera.getConfig(),
            "À propos": self.camera.getAbout(),
            "Sommaire": self.camera.getSummary(),
        }
        displayStr = ""
        for name, obj in propertiesDict.items():
            displayStr += f"\n<h3>{name}</h3>\n"
            displayStr += self.htmlTablize(self.filteredDir(obj))

        self.PropertiesText.setText(displayStr)
