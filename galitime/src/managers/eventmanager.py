#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module for folder management
"""

import json
import logging
import os
import re
import shutil

from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtWidgets import QMainWindow

from ..managers.emailmanager import EmailManager
from ..managers.photomanager import PhotoManager
from ..utilities.constants import DATE_FORMAT, ENCODING
from ..utilities.constants import EVENT_SAVE_FILE

logger = logging.getLogger(__name__)
logger.propagate = True


class EventManager:
    """
    FolderManager : Class aimed at maganing the eventFolder
    """

    saveFolder = ""
    eventName = ""
    eventDate = ""
    photoNumber = 0
    eventOpened = False

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
        setEventDate : sets the event date to the supplied date with the specified
        format

        Args:
            eventDate (str): evant date with the format yyyy-MM-dd (year-month-day)
        """
        checkRegEx = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        if not re.match(checkRegEx, eventDate):
            raise SyntaxError("Date format not valid, must respect yyyy-MM-dd format")
        cls.eventDate = eventDate

    @classmethod
    def setEventOpened(cls, eventOpened: bool) -> None:
        """
        setEventOpened : Sets the event opened variable to mark event as opened

        Args:
            eventOpened (bool): Event state
        """
        cls.eventOpened = eventOpened

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
        getEventDate : returns the event date with the format yyyy-MM-dd (
        year-month-day)
        """
        return cls.eventDate

    @classmethod
    def isEventOpened(cls) -> bool:
        """
        isEventOpened : returns true if the event is opened, false otherwise
        """
        return cls.eventOpened

    @staticmethod
    def createFolderScructure(saveFolder: str) -> None:
        """
        createFolderScructure : Create folder structure of an event folder

        Args:
            saveFolder (str): folder path in witch the event file structure will be
            created
        """
        logger.debug("Creating new event folder structure in folder %s", saveFolder)
        os.mkdir(saveFolder)
        os.mkdir(saveFolder + "raw_photos")
        os.mkdir(saveFolder + "emails")

        EmailManager.setEmailFolder(saveFolder + "emails")
        PhotoManager.setPhotoFolder(saveFolder + "raw_photos")
        logger.info(
            "Successfully created new event folder structure in folder %s", saveFolder
        )

    @classmethod
    def updateInfoFile(cls) -> None:
        """
        writeInfoFile : Write event info to the save file
        """
        infoDict = {
            "eventName": cls.getEventName(),
            "eventDate": cls.getEventDate(),
            "photoNumber": PhotoManager.getPhotoNumber(),
            "emailNumber": EmailManager.getEmailNumber(),
        }
        cls._writeInfoFile(infoDict)
        logger.debug("Event info file updated")

    @classmethod
    def _writeInfoFile(cls, infodict: dict) -> None:
        """
        _writeInfoFile: Write supplied dictionnary to info file in it's json
        representation.

        Args:
            infodict (dict): event info dict to write.
        """
        with open(cls.saveFolder + EVENT_SAVE_FILE, "wt", encoding=ENCODING) as file:
            json.dump(infodict, file, indent=4)

    @classmethod
    def _readInfoFile(cls) -> dict:
        """
        _readInfoFile : Reads the event info file and return a dict representation of
        it's json content

        Returns:
            dict: json content of info file
        """
        with open(cls.saveFolder + EVENT_SAVE_FILE, "rt", encoding=ENCODING) as file:
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

        logger.debug("Attempting to create new event folder at %s", saveFolder)

        name = os.path.dirname(saveFolder)
        path = os.path.basename(saveFolder)

        if os.path.exists(saveFolder):
            if not overwrite:
                yesNoButton = QMessageBox.question(
                    cls.parent,
                    "Folder already exists",
                    f"""Folder {name} already exists in f{path}
                    Do you want to overwrite it ? All previous data will be lost""", )
                if yesNoButton != QMessageBox.Yes:
                    return

            logger.info("Removing pre-existing folder %s and it's contents", saveFolder)
            shutil.rmtree(saveFolder)

        cls.createFolderScructure(saveFolder)
        cls.updateInfoFile()
        logger.info("Created new event folder at %s", saveFolder)

    @classmethod
    def loadSaveFolder(cls, folder: str = None) -> bool:
        """
        loadSaveFolder : Loads event information from the folder supplied via
        "folder" argument.
        If None is supplied, user will be prompt with a file dialog to choose it.

        Args:
            folder (str, optional): File path to the event folder that should be loaded.
                                    Defaults to None.

        Returns:
            bool: True if the folder was successfully loaded, False instead.
        """
        if folder is None or not isinstance(folder, str):
            folder = QFileDialog.getExistingDirectory(
                cls.parent, caption="Select an Event Folder"
            )

        if len(folder) == 0:
            QMessageBox.critical(
                cls.parent, "Invalid folder path", "Folder path should not be empty"
            )
            return False
        folder += "/"

        logger.debug("Loading folder %s", folder)

        if not os.path.exists(folder + EVENT_SAVE_FILE):
            QMessageBox.critical(
                cls.parent,
                "Loading error",
                f"No {EVENT_SAVE_FILE} file found in\n{folder}\n Aborting load "
                f"operation\n\nInvalid folder", )
            return False
        cls.saveFolder = folder

        with open(folder + EVENT_SAVE_FILE, "rt", encoding=ENCODING) as file:
            infoDict = json.load(file)

        # File structure check
        if not os.path.exists(cls.saveFolder + "raw_photos"):
            QMessageBox.warning(
                cls.parent,
                "Loading error",
                f"No raw_photos in \n{folder}\n Creating an empty one\n\nraw_photos "
                f"folder missing", )
            os.mkdir(cls.saveFolder + "raw_photos")
        PhotoManager.photoFolder = cls.saveFolder + "raw_photos/"

        if not os.path.exists(cls.saveFolder + "emails"):
            QMessageBox.warning(
                cls.parent, "Loading error", f"""No emails in {folder}
                Creating an empty one
                'emails/' folder missing""", )
            os.mkdir(cls.saveFolder + "emails")
        EmailManager.setEmailFolder(cls.saveFolder + "emails/")

        # Content checking

        defaultValue = "EVENT (default name)"
        if "eventName" not in infoDict.keys():
            QMessageBox.critical(
                cls.parent, "Invalid info file", f'Property "eventName" missing from '
                                                 f'info file, \
                    returning to default value: {defaultValue}', )
            infoDict["eventName"] = defaultValue
        cls.setEventName(infoDict["eventName"])

        defaultValue = QDate.currentDate().toString(DATE_FORMAT)
        if "eventDate" not in infoDict.keys():
            QMessageBox.critical(
                cls.parent, "Invalid info file", f'Property "eventDate" missing from '
                                                 f'info file, \
                    returning to default value: {defaultValue}', )
            infoDict["eventDate"] = defaultValue
        cls.setEventDate(infoDict["eventDate"])

        logger.debug("Loaded folder successfully")

        cls.updateInfoFile()

        return True

EmailManager.setEventManager(EventManager)