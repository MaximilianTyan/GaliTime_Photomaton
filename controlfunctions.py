#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module containing functionnality functions for the controlwindow.py module. 
The two are kept separated for readability.
"""

import os
import inspect
import logging
import json

from PyQt5.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from PyQt5.QtCore import QDate, QTimer
import ressources.stylesheet as stylesheet

logger = logging.getLogger(__name__)
logger.propagate = True

ENCODING = "utf-8"
DATEFORMAT = "yyyy-MM-dd"
TEMPFILE = "{}/temp.jpeg"


def init(self, screen, cam, printer) -> None:
    """init : Initialises control functions variables and objects"""
    self.screen = screen
    self.cam = cam
    self.printer = printer

    self.eventName = ""
    self.eventDate = ""

    self.saveFolder = ""
    self.photoFolder = ""
    self.emailFolder = ""

    self.crtPhotoPath = ""

    self.photoNumber = 0
    self.emailNumber = 0

    self.eventOpened = False

    self.timer = QTimer()
    self.timer.timeout.connect(lambda: tickTimer(self))


# Options page


def choosesaveFolderPath(self) -> None:
    """
    choosesaveFolderPath : Prompts the user with a file dialog to choose
    the save folder where to save the event.
    """
    parentFolderPath = QFileDialog.getExistingDirectory(
        self, caption="Dossier d'enregistrement"
    )

    self.saveFolder = f"{parentFolderPath}/{self.eventName}/"
    self.saveFolderPathLabel.setText("Dossier d'enregistrement:\n" + self.saveFolder)


def chooseDecorFile(self) -> None:
    """
    chooseDecorFile : Prompts the user with a file dialog to choose the
    save folder where to save the event.
    """
    output = QFileDialog.getOpenFileName(self, caption="Image de décor")
    self.screen.setDecorFile(output[0])
    self.DecorFileLabel.setText("Image de décor:\n" + self.screen.getDecorFile())


def changeEventName(self) -> None:
    """
    changeEventName : Retrieves the event name from the text input and
    saves it as event name
    """
    if self.EventInput.text().strip() != "":
        self.eventName = self.EventInput.text()
        self.EventInput.setStyleSheet("background-color: rgb(100, 200, 100)")
    else:
        self.EventInput.setStyleSheet("background-color: rgb(200, 100, 100)")


def changeEventDate(self) -> None:
    """
    changeEventDate : Retrieves the event name from the text input and 
    saves it as event name
    """
    date = self.EventDateInput.date()
    if date.isValid():
        self.eventDate = date.toString(DATEFORMAT)
        self.EventDateInput.setStyleSheet("background-color: rgb(100, 200, 100)")
    else:
        self.EventDateInput.setStyleSheet("background-color: rgb(200, 100, 100)")


# Page switch


def controlPageCheck(self) -> None:
    """
    controlPageCheck : Checks if all required information for event loading was 
    provided and displays an error message if any is missing
    """
    if self.eventName.strip() == "":
        self.errorLabel.setText("Le nom de l'événement ne doit pas être vide")
        return
    if self.eventDate is None:
        self.errorLabel.setText("La date de l'événement doit être validée")
        return
    if self.saveFolder.strip() == "":
        self.errorLabel.setText("Le dossier d'enregistrement doit être valide")
        return
    if self.screen.getDecorFile().strip() == "":
        self.errorLabel.setText("Le fichier de décoration doit être valide")
        return

    initSaveFolder(self)

    if not self.eventOpened:
        self.screen.startPreview()
        self.eventOpened = True

    self.controlPage()


def cancelOptions(self) -> None:
    """
    cancelOptions : Return function for the option page, returns either to the 
    control page if an event is opened, to start page otherwise
    """
    if self.eventOpened:
        self.controlPage()
    else:
        self.startPage()


# Folder management


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


def initSaveFolder(self) -> None:
    """
    initSaveFolder : Create an event folder at the saveFolder path.
    """
    name = self.saveFolder.split("/")[-2] + "/"
    path = self.saveFolder.rstrip(name)

    if os.path.exists(self.saveFolder):
        YNButton = QMessageBox.question(
            self,
            "Folder already exists",
            f"""Folder {name} already exists in f{path}
            Do you want to overwrite it ? All previous data will be lost""",
        )
        if YNButton != QMessageBox.Yes:
            return

        for file in os.listdir(self.saveFolder):
            os.remove(self.saveFolder + file)

    createFolderScructure(self.saveFolder)
    writeInfoFile(self)


def createFolderScructure(saveFolder: str) -> None:
    """
    createFolderScructure : Create folder structure of an event folder

    Args:
        saveFolder (str): folder path in witch the event file structure will be created
    """
    os.mkdir(saveFolder)
    os.mkdir(saveFolder + "raw_photos")
    os.mkdir(saveFolder + "emails")


# Info file


def writeInfoFile(self) -> None:
    """
    writeInfoFile : Write event info to the save file
    """
    infodict = {
        "eventName": self.eventName,
        "eventDate": self.eventDate,
        "saveFolder": self.saveFolder,
        "photoNumber": self.photoNumber,
        "emailNumber": self.emailNumber,
    }
    with open(self.saveFolder + "info.json", "wt", encoding=ENCODING) as file:
        json.dump(infodict, file, indent=4)


# Timer functions


def photoButton(self) -> None:
    """
    photoButton : Function linked to the photoButton, either starts
    the timer countdown or returns to previewing
    """
    if self.screen.isPreviewing():
        self.PhotoButton.setEnabled(False)
        self.PhotoButton.setStyleSheet(stylesheet.BigDisabledButton)
        startCountdown(self)
    else:
        self.PhotoButton.setText("Prendre la photo")
        self.screen.startPreview()


def startCountdown(self) -> None:
    """
    startCountdown : Starts the photo countdown
    """
    if self.timer.isActive():
        return

    self.timer.countdown = 3
    self.timer.start(1000)
    logger.info("Photo countdown started")


def tickTimer(self) -> None:
    """
    tickTimer : callback function to tick the photo countdown timer
    """
    if self.timer.countdown < 0:
        self.timer.stop()
        # Timer end
        self.screen.showText("")
        takePhoto(self)

        self.PhotoButton.setEnabled(True)
        self.PhotoButton.setStyleSheet(stylesheet.BigBlueButton)
        self.PhotoButton.setText("Revenir à l'aperçu")

        logger.info("Photo countdown ended")
    elif self.timer.countdown == 0:
        self.screen.showText("SOURIEZ")
    else:
        self.screen.showText(self.timer.countdown)

    self.timer.countdown -= 1


# Photo functions


def takePhoto(self):
    self.screen.stopPreview()
    rawPhoto = self.cam.takePhoto(self.photoFolder)
    self.screen.displayImage(rawPhoto)

    self.photoNumber += 1
    self.crtPhotoPath = self.screen.saveImage(TEMPFILE.format(self.saveFolder))


def printImage(self):
    self.printer.printImage(self.crtPhotoPath)


# Camera utilities


def reconnectCamera(self):
    # self.cam.__init__()
    self.cam.connect()


def updateCamList(self):
    self.CamsChoiceBox.clear()
    cam_list = self.cam.listCams()

    if len(cam_list) == 0 or cam_list is None:
        self.CamsChoiceBox.addItem("None")

    for cam in cam_list:
        for i in cam:
            self.CamsChoiceBox.addItem(i)


def filteredDir(obj):
    outdict = {}

    for attr in dir(obj):
        if attr.startswith("_"):
            continue

        if attr in ("acquire", "append", "disown", "next", "own", "this", "thisown"):
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
def HTMLTablize(datadict) -> str:
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
    camAbilities = filteredDir(self.cam.getAbilities())
    self.AbilitiesText.setText(HTMLTablize(camAbilities))


def updateConfig(self) -> None:
    camConfig = filteredDir(self.cam.getCconfig())
    self.ConfigText.setText(HTMLTablize(camConfig))


def updateAbout(self) -> None:
    camAbout = filteredDir(self.cam.getAbout())
    self.AboutText.setText(HTMLTablize(camAbout))


def updateSummary(self) -> None:
    camSummary = filteredDir(self.cam.getSummary())
    self.SummaryText.setText(HTMLTablize(camSummary))
