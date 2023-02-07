#!/bin/env python3
# coding:utf-8
# encoding:utf-8

""" Module for email handling
"""

import os
import json
import logging
import shutil

from PyQt5.QtWidgets import QInputDialog

logger = logging.getLogger(__name__)
logger.propagate = True

ENCODING = "utf-8"
INFOFILE = "email.json"


class EmailManager:
    """emailManager : Class responsible for managing mail storage and access"""

    def __init__(self, emailFolder: str) -> None:
        self.setEmailFolder(emailFolder)
        self.emailNumber = len(os.listdir(emailFolder))

    def setEmailFolder(self, folderpath: str) -> None:
        """setEmailFolder : Sets the emails folder path

        Args:
            folderpath (str): folderpath to the emails folder
        """
        if not folderpath.endswith("/"):
            folderpath += "/"
        self.emailFolder = folderpath

    def createMail(self, mail: str) -> str:
        """createMail : Creates a folder for the supplied email

        Args:
            mail (str): email in the form example@domain.xxx

        Returns:
            str: folderpath to the email folder
        """
        mailPath = self.emailFolder + mail.replace("/", " ")
        os.mkdir(mailPath)

        mailDict = {
            "email": mail,
            "photoNumber": 0,
        }
        with open(mailPath + "/email.json", "wt", encoding=ENCODING) as file:
            json.dump(mailDict, file, indent=4)
        self.emailNumber += 1

        return mailPath

    def getMail(self, mail: str) -> str:
        """getMail : Retrieves folderpath to the mail folder.

        Args:
            mail (str): email in the form example@domain.xxx

        Returns:
            str: Filepath to the email folder, empty string if not found.
        """
        mailPath = self.emailFolder + mail.replace("/", " ")
        if not os.path.exists(mailPath):
            return ""
        return mailPath

    def _readEmailInfo(self, mail: str) -> dict:
        """_readEmailInfo : Returns email info json file as dict object.

        Args:
            mail (str):  email in the form example@domain.xxx

        Returns:
            dict: Python representation of the JSON file
        """
        with open(
            self.emailFolder + mail + "/" + INFOFILE, "rt", encoding=ENCODING
        ) as file:
            return json.load(file)

    def _writeEmailInfo(self, infoDict: dict) -> None:
        """_writeEmailInfo _summary_

        Args:
            infoDict (dict): _description_
        """
        with open(self.emailFolder + INFOFILE, "wt", encoding=ENCODING) as file:
            json.dump(file, infoDict)

    def addPhotoToMail(self, photoPath: str) -> None:
        """addPhotoToMail

        Args:
            photoPath (str): photo filepath to add to email
        """
        mailStr = QInputDialog.getText(
            self,
            "Emails (séparés par des virgules)",
            "Votre ou vos emails séparés par des virgules",
        )
        mailList = [mail.strip() for mail in mailStr.split(",")]

        for mail in mailList:

            mailPath = self.getMail(mail)
            if len(mailPath) == 0:
                mailPath = self.createMail(mail)

            if len(photoPath) == 0:
                logger.error("No photo supplied")
                return

            shutil.copy(photoPath, mailPath)

            mailDict = self._readEmailInfo(mail)
            mailDict["photoNumber"] += 1
            self._writeEmailInfo(mailDict)
