#!/bin/env python3
#encoding:utf-8
#coding:utf-8

"""
Module for folder management
"""

import os
import json
import logging
import re
import shutil

from PyQt5.QtWidgets import QFileDialog, QMessageBox

logger = logging.getLogger(__name__)
logger.propagate = True

ENCODING = "utf-8"
SAVEFILE = "event.json"
DATEFORMAT = "yyyy-MM-dd"


class EventManager():
    """
    FolderManager : Class aimed at maganing the eventFolder
    """
    def __init__(self, eventName:str, eventFolder:str="") -> None:
        self.saveFolder = eventFolder
        self.eventName = eventName
        self.eventDate = ""
        
    def setEventFolder(self, eventFolder:str) -> None:
        """
        setEventFolder : set event folder path

        Args:
            eventFolder (str): folderpath
        """
        if not eventFolder.endswith('/'):
            eventFolder += '/'
        self.saveFolder = eventFolder
    
    def setEventName(self, eventName:str) -> None:
        """
        setEventName : sets the event name to the stripped given name

        Args:
            eventName (str): event name
        """
        self.eventName = eventName.strip()
    
    def setEventDate(self, eventDate:str) -> None:
        """
        setEventDate : sets the event date to the supplied date with the specified format

        Args:
            eventDate (str): evant date with the format yyyy-MM-dd (year-month-day)
        """
        checkRegEx = "^[0-9]{4}-[0-9]{2}-[0-9]{2}$"
        if not re.match(checkRegEx, eventDate):
            raise SyntaxError("Date format not valid, must respect yyyy-MM-dd format")
        self.eventDate = eventDate
    
    @staticmethod
    def createFolderScructure(saveFolder:str) -> None:
        """
        createFolderScructure : Create folder structure of an event folder

        Args:
            saveFolder (str): folder path in witch the event file structure will be created
        """
        os.mkdir(saveFolder)
        os.mkdir(saveFolder + "raw_photos")
        os.mkdir(saveFolder + "emails")

    def updateInfoFile(self, dict) -> None:
        """
        writeInfoFile : Write event info to the save file
        """
        infoDict = {
            "eventName": self.eventName,
            "eventDate": self.eventDate,
            "saveFolder": self.saveFolder,
            "photoNumber": self.photoNumber,
            "emailNumber": self.emailNumber,
        }
        self._writeInfoFile(infoDict)

    def _writeInfoFile(self, infodict:dict) -> None:
        """
        _writeInfoFile : Write supplied dictionnary to info file in it's json representation.

        Args:
            infodict (dict): event info dict to write.
        """
        with open(self.saveFolder + SAVEFILE, "wt", encoding=ENCODING) as file:
            json.dump(infodict, file, indent=4)
    
    def _readInfoFile(self) -> dict:
        """
        _readInfoFile : Reads the event info file and return a dict representation of it's json content

        Returns:
            dict: json content of info file
        """
        with open(self.saveFolder + SAVEFILE, "rt", encoding=ENCODING) as file:
            return json.load(file)

    def initSaveFolder(self, saveFolder:str, overwrite:bool=False) -> None:
        """
        initSaveFolder : Create an event folder at the saveFolder path.

        Args:
            saveFolder (str): folder path a saveFolder will be created
            overwrite (bool, optional): if . Defaults to False.
        """

        if saveFolder.endswith('/'):
            saveFolder = saveFolder.rstrip('/')

        name = os.path.dirname(saveFolder)
        path = os.path.basename(saveFolder)

        if os.path.exists(saveFolder):
            if not overwrite:
                yesNoButton = QMessageBox.question(
                    self,
                    "Folder already exists",
                    f"""Folder {name} already exists in f{path}
                    Do you want to overwrite it ? All previous data will be lost""",
                )
                if yesNoButton != QMessageBox.Yes:
                    return

            shutil.rmtree(saveFolder)

        self.createFolderScructure(saveFolder)
        self._writeInfoFile()


def loadSaveFolder(self, folder: str = None) -> None:
    """
    loadSaveFolder : Loads event information from the folder supplied via "folder" argument.
    If None is supplied, user will be prompt with a file dialog to choose it.

    Args:
        folder (str, optional): File path to the event folder that should be loaded.
                                Defaults to None.
    """
    if folder is None:
        folder = QFileDialog.getExistingDirectory(
            self, caption="Select an Event Folder"
        )

    if len(folder) == 0:
        return
    folder += "/"

    logger.debug("Loading folder %s", folder)

    if not os.path.exists(folder + "info.json"):
        QMessageBox.critical(
            self,
            "Loading error",
            f"No info.json file found in\n{folder}\n Aborting load operation\n\nInvalid folder",
        )
        return

    with open(folder + "info.json", "rt", encoding=ENCODING) as file:
        infoDict = json.load(file)

    # File structure checking
    self.saveFolder = infoDict.get("saveFolder", None)
    if self.saveFolder is None:
        QMessageBox.critical(
            self,
            "Loading error",
            """No save folder was supplied in info.json
            Aborting load operation\n
            No save folder supplied""",
        )
        return

    if not os.path.exists(self.saveFolder):
        QMessageBox.critical(
            self,
            "Loading error",
            """Save folder supplied in info.json does not exist
            Aborting load operation\n
            Save folder does not exist""",
        )
        return

    if not os.path.exists(self.saveFolder + "raw_photos"):
        QMessageBox.warning(
            self,
            "Loading error",
            f"No raw_photos in \n{folder}\n Creating an empty one\n\nraw_photos folder missing",
        )
        os.mkdir(self.saveFolder + "raw_photos")
    self.photoFolder = self.saveFolder + "raw_photos/"

    if not os.path.exists(self.saveFolder + "emails"):
        QMessageBox.warning(
            self,
            "Loading error",
            f"""No emails in {folder}
            Creating an empty one
            'emails/' folder missing""",
        )
        os.mkdir(self.saveFolder + "emails")
    self.emailFolder = self.saveFolder + "emails/"

    # Content checking
    requiredKeys = {
        "eventName": "Event (DEFAULT NAME)",
        "eventDate": QDate.currentDate().toString(DATEFORMAT),
        "saveFolder": self.saveFolder,
        "photoNumber": len(os.listdir(self.photoFolder)),
        "emailNumber": len(os.listdir(self.emailFolder)),
    }

    for attr, attrValue in requiredKeys.items():
        if attr not in infoDict.keys():
            QMessageBox.critical(
                self,
                "Invalid info file",
                f'Property "{attr}" missing from info file, \
                returning to default value: {attrValue}',
            )
            object.__setattr__(self, attr, attrValue)
        else:
            object.__setattr__(self, attr, infoDict[attr])

    logger.debug("Loaded folder successfully")

    writeInfoFile(self)
    self.optionsPage()
    changeEventName(self)
    changeEventDate(self)