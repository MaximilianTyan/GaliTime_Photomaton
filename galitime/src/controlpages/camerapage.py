#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module managing the camera options page
"""

import inspect
import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QPushButton, QTextEdit
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

        # 2 Available cameras Layout
        CamsHLayout = QHBoxLayout()
        MainVLayout.addLayout(CamsHLayout)

        # 2.1 Choice box listing items
        self.CamsChoiceBox = QComboBox()
        self.updateCamList()
        CamsHLayout.addWidget(self.CamsChoiceBox)

        # 2.2 Update button
        CamsUpdateButton = QPushButton("MAJ Liste caméra")
        CamsUpdateButton.clicked.connect(self.updateCamList)
        CamsHLayout.addWidget(CamsUpdateButton)

        # 3 Info Grid Layout
        AbilitiesVLayout = QVBoxLayout()
        MainVLayout.addLayout(AbilitiesVLayout)

        # 3.1 Abilities list button
        AbilitiesUpdateButton = QPushButton("Mise à jour")
        AbilitiesUpdateButton.clicked.connect(self.updateAll)
        AbilitiesVLayout.addWidget(AbilitiesUpdateButton)

        # 3.1 Abilities list button
        self.PropertiesText = QTextEdit()
        AbilitiesVLayout.addWidget(self.PropertiesText)

        # 4 Reconnect Return layout
        ReconnectReturnLayout = QHBoxLayout()
        MainVLayout.addLayout(ReconnectReturnLayout)

        # 4. Reconnect camera button
        self.ReconnectButton = QPushButton("Reconnexion caméra")
        self.ReconnectButton.setStyleSheet(cssify("Big Disabled"))
        self.ReconnectButton.clicked.connect(self.reconnectCamera)
        ReconnectReturnLayout.addWidget(self.ReconnectButton)
        self.updateReconnectButton()

        # 5 Return button
        ReturnButton = QPushButton("Retour")
        ReturnButton.setStyleSheet(cssify("Big Red"))
        ReturnButton.clicked.connect(lambda: self.mainWindow.loadPage(PageEnum.CONTROL))
        ReconnectReturnLayout.addWidget(ReturnButton)

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
            self.ReconnectButton.setStyleSheet(cssify("Big Blue"))
            self.ReconnectButton.setEnabled(True)
        else:
            self.ReconnectButton.setStyleSheet(cssify("Big Disabled"))
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
        text = "<table>\n \
                    <tr> \n \
                        <td> Attribute </td>\n \
                        <td> Value </td>\n \
                    </tr>\n"

        for key, value in datadict.items():
            text += f"<tr> \n \
                        <td> {key} </td>\n \
                        <td> {value} </td>\n \
                    </tr>\n"

        text += "<table>"
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
