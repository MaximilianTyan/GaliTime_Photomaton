#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module for folder management
"""

import os
import json
import logging
import re
import shutil

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QDate

from emailmanager import EmailManager

from constants import DATEFORMAT, ENCODING

logger = logging.getLogger(__name__)
logger.propagate = True

SAVEFILE = "event.json"


class EventManager:
    """
    FolderManager : Class aimed at maganing the eventFolder
    """

    saveFolder = ""
    eventName = ""
    eventDate = ""
    photoNumber = 0

    parent = None

    @classmethod
    def setParentWindow(cls, Window: QMainWindow) -> None:
        """
        setParentWindow : Sets the parent window to allow for pop ups and dialogues

        Args:
            Window (QMainWindow): Deault parent window above which dialoges will appear
        """
        cls.parent = Window

    @classmethod
    def setEventFolder(cls, eventFolder: str) -> None:
        """
        setEventFolder : set event folder path

        Args:
            eventFolder (str): folderpath
        """
        if not eventFolder.endswith("/"):
            eventFolder += "/"
        cls.saveFolder = eventFolder

    @classmethod
    def setEventName(cls, eventName: str) -> None:
        """
        setEventName : sets the event name to the stripped given name

        Args:
            eventName (str): event name
        """
        cls.eventName = eventName.strip()

    @classmethod
    def setEventDate(cls, eventDate: str) -> None:
        """
        setEventDate : sets the event date to the supplied date with the specified format

        Args:
            eventDate (str): evant date with the format yyyy-MM-dd (year-month-day)
        """
        checkRegEx = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        if not re.match(checkRegEx, eventDate):
            raise SyntaxError("Date format not valid, must respect yyyy-MM-dd format")
        cls.eventDate = eventDate

    @classmethod
    def incrementPhotoNumber(cls, increment: int = 1) -> None:
        """
        incrementPhotoNumber : Increments the photo number by the given value

        Args:
            increment (int, optional): Incrementation value. Defaults to 1.
        """
        cls.photoNumber += increment

    @classmethod
    def getEventFolder(cls) -> str:
        """
        setEventFolder : returns the event folder path
        """
        return cls.saveFolder

    @classmethod
    def getEventName(cls) -> str:
        """
        getEventName : returns the event name
        """
        return cls.eventName

    @classmethod
    def getEventDate(cls) -> str:
        """
        getEventDate : returns the event date with the format yyyy-MM-dd (year-month-day)
        """
        return cls.eventDate

    @staticmethod
    def createFolderScructure(saveFolder: str) -> None:
        """
        createFolderScructure : Create folder structure of an event folder

        Args:
            saveFolder (str): folder path in witch the event file structure will be created
        """
        os.mkdir(saveFolder)
        os.mkdir(saveFolder + "raw_photos")
        os.mkdir(saveFolder + "emails")

    @classmethod
    def updateInfoFile(cls) -> None:
        """
        writeInfoFile : Write event info to the save file
        """
        infoDict = {
            "eventName": cls.eventName,
            "eventDate": cls.eventDate,
            "saveFolder": cls.saveFolder,
            "photoNumber": cls.photoNumber,
            "emailNumber": EmailManager.getEmailNumber(),
        }
        cls._writeInfoFile(infoDict)

    @classmethod
    def _writeInfoFile(cls, infodict: dict) -> None:
        """
        _writeInfoFile : Write supplied dictionnary to info file in it's json representation.

        Args:
            infodict (dict): event info dict to write.
        """
        with open(cls.saveFolder + SAVEFILE, "wt", encoding=ENCODING) as file:
            json.dump(infodict, file, indent=4)

    @classmethod
    def _readInfoFile(cls) -> dict:
        """
        _readInfoFile : Reads the event info file and return a dict representation of it's json content

        Returns:
            dict: json content of info file
        """
        with open(cls.saveFolder + SAVEFILE, "rt", encoding=ENCODING) as file:
            return json.load(file)

    @classmethod
    def initSaveFolder(cls, saveFolder: str, overwrite: bool = False) -> None:
        """
        initSaveFolder : Create an event folder at the saveFolder path.

        Args:
            saveFolder (str): folder path a saveFolder will be created
            overwrite (bool, optional): if . Defaults to False.
        """

        if not saveFolder.endswith("/"):
            saveFolder += "/"

        name = os.path.dirname(saveFolder)
        path = os.path.basename(saveFolder)

        if os.path.exists(saveFolder):
            if not overwrite:
                yesNoButton = QMessageBox.question(
                    cls.parent,
                    "Folder already exists",
                    f"""Folder {name} already exists in f{path}
                    Do you want to overwrite it ? All previous data will be lost""",
                )
                if yesNoButton != QMessageBox.Yes:
                    return

            shutil.rmtree(saveFolder)

        cls.createFolderScructure(saveFolder)
        cls.updateInfoFile()

    @classmethod
    def loadSaveFolder(cls, folder: str = None) -> None:
        """
        loadSaveFolder : Loads event information from the folder supplied via "folder" argument.
        If None is supplied, user will be prompt with a file dialog to choose it.

        Args:
            folder (str, optional): File path to the event folder that should be loaded.
                                    Defaults to None.
        """
        if folder is None or not isinstance(folder, str):
            folder = QFileDialog.getExistingDirectory(
                cls.parent, caption="Select an Event Folder"
            )

        if len(folder) == 0:
            return
        folder += "/"

        logger.debug("Loading folder %s", folder)

        if not os.path.exists(folder + "info.json"):
            QMessageBox.critical(
                cls.parent,
                "Loading error",
                f"No info.json file found in\n{folder}\n Aborting load operation\n\nInvalid folder",
            )
            return

        with open(folder + "info.json", "rt", encoding=ENCODING) as file:
            infoDict = json.load(file)

        # File structure checking
        cls.saveFolder = infoDict.get("saveFolder", None)
        if cls.saveFolder is None:
            QMessageBox.critical(
                cls.parent,
                "Loading error",
                """No save folder was supplied in info.json
                Aborting load operation\n
                No save folder supplied""",
            )
            return

        if not os.path.exists(cls.saveFolder):
            QMessageBox.critical(
                cls.parent,
                "Loading error",
                """Save folder supplied in info.json does not exist
                Aborting load operation\n
                Save folder does not exist""",
            )
            return

        if not os.path.exists(cls.saveFolder + "raw_photos"):
            QMessageBox.warning(
                cls.parent,
                "Loading error",
                f"No raw_photos in \n{folder}\n Creating an empty one\n\nraw_photos folder missing",
            )
            os.mkdir(cls.saveFolder + "raw_photos")
        cls.photoFolder = cls.saveFolder + "raw_photos/"

        if not os.path.exists(cls.saveFolder + "emails"):
            QMessageBox.warning(
                cls.parent,
                "Loading error",
                f"""No emails in {folder}
                Creating an empty one
                'emails/' folder missing""",
            )
            os.mkdir(cls.saveFolder + "emails")
        EmailManager.setEmailFolder(cls.saveFolder + "emails/")

        # Content checking
        requiredKeys = {
            "eventName": "Event (DEFAULT NAME)",
            "eventDate": QDate.currentDate().toString(DATEFORMAT),
            "saveFolder": cls.saveFolder,
            "photoNumber": len(os.listdir(cls.photoFolder)),
        }

        for attr, attrValue in requiredKeys.items():
            if attr not in infoDict.keys():
                QMessageBox.critical(
                    cls.parent,
                    "Invalid info file",
                    f'Property "{attr}" missing from info file, \
                    returning to default value: {attrValue}',
                )
                object.__setattr__(cls, attr, attrValue)
            else:
                object.__setattr__(cls, attr, infoDict[attr])

        logger.debug("Loaded folder successfully")

        cls.updateInfoFile()
