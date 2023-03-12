#!/bin/env python3
# encoding:utf-8
# coding:utf-8

import logging
import inspect

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtWidgets import QPushButton, QComboBox, QTextEdit

import stylesheet
from camera import CameraWrapper

logger = logging.getLogger(__name__)
logger.propagate = True


class CameraPage:
    """
    StartPage : Handles camera page functionnality
    """

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow
        self.camera = CameraWrapper.getCamera()

        self.CamsChoiceBox = None
        self.AbilitiesText = None
        self.AbilitiesText = None
        self.ConfigText = None
        self.AboutText = None
        self.SummaryText = None

    def load(self):
        """
        load : Loads the camera page in a QWidget and returns it

        Returns:
            PyQt5.QtWidget: Camera page loaded layout
        """
        logger.debug("Loading camera options page")
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
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
        InfoGridLayout = QGridLayout()
        MainVLayout.addLayout(InfoGridLayout)

        # 3.1 Abilities Layout
        AbilitiesVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(AbilitiesVLayout, 0, 0)

        # 3.1.1 Abilities list button
        AbilitiesUpdateButton = QPushButton("MAJ Abilities")
        AbilitiesUpdateButton.clicked.connect(self.updateAbilities)
        AbilitiesVLayout.addWidget(AbilitiesUpdateButton)

        # 3.1.2 Abilities list button
        self.AbilitiesText = QTextEdit()
        AbilitiesVLayout.addWidget(self.AbilitiesText)

        # 3.2 Config Layout
        ConfigVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(ConfigVLayout, 0, 1)

        # 3.2.1 Config list button
        ConfigUpdateButton = QPushButton("MAJ Config")
        ConfigUpdateButton.clicked.connect(self.updateConfig)
        ConfigVLayout.addWidget(ConfigUpdateButton)

        # 3.2.2 Config list button
        self.ConfigText = QTextEdit()
        ConfigVLayout.addWidget(self.ConfigText)

        # 3.3 About Layout
        AboutVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(AboutVLayout, 1, 0)

        # 3.3.1 About list button
        AboutUpdateButton = QPushButton("MAJ About")
        AboutUpdateButton.clicked.connect(self.updateAbout)
        AboutVLayout.addWidget(AboutUpdateButton)

        # 3.3.2 About list button
        self.AboutText = QTextEdit()
        AboutVLayout.addWidget(self.AboutText)

        # 3.4 Summary Layout
        SummaryVLayout = QVBoxLayout()
        InfoGridLayout.addLayout(SummaryVLayout, 1, 1)

        # 3.4.1 Summary list button
        SummaryUpdateButton = QPushButton("MAJ Summary")
        SummaryUpdateButton.clicked.connect(self.updateSummary)
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
        ReconnectButton.clicked.connect(self.reconnectCamera)
        ReconnectReturnLayout.addWidget(ReconnectButton)

        # 5 Return button
        ReturnButton = QPushButton("Retour")
        ReturnButton.setStyleSheet(stylesheet.BigRedButton)
        ReturnButton.clicked.connect(lambda: self.mainWindow.loadPage("control"))
        ReconnectReturnLayout.addWidget(ReturnButton)

        logger.debug("Camera options page loaded")
        return MainContainer

    def reconnectCamera(self):
        # self.cam.__init__()
        self.camera.connect()

    def updateCamList(self):
        self.CamsChoiceBox.clear()
        cam_list = self.camera.listCams()

        if len(cam_list) == 0 or cam_list is None:
            self.CamsChoiceBox.addItem("None")

        for cam in cam_list:
            for i in cam:
                self.CamsChoiceBox.addItem(i)

    @staticmethod
    def filteredDir(obj):
        outdict = {}

        for attr in dir(obj):
            if attr.startswith("_"):
                continue

            if attr in (
                "acquire",
                "append",
                "disown",
                "next",
                "own",
                "this",
                "thisown",
            ):
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
        HTMLTablize : Formats the given dictionnary into a HTML table

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

    def updateAbilities(self) -> None:
        camAbilities = self.filteredDir(self.camera.getAbilities())
        self.AbilitiesText.setText(self.htmlTablize(camAbilities))

    def updateConfig(self) -> None:
        camConfig = self.filteredDir(self.camera.getConfig())
        self.ConfigText.setText(self.htmlTablize(camConfig))

    def updateAbout(self) -> None:
        camAbout = self.filteredDir(self.camera.getAbout())
        self.AboutText.setText(self.htmlTablize(camAbout))

    def updateSummary(self) -> None:
        camSummary = self.filteredDir(self.camera.getSummary())
        self.SummaryText.setText(self.htmlTablize(camSummary))
