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

from constants import ENCODING, INFOFILE

logger = logging.getLogger(__name__)
logger.propagate = True


class EmailManager:
    """emailManager : Class responsible for managing mail storage and access"""

    emailFolder = None

    @classmethod
    def setEmailFolder(cls, folderpath: str) -> None:
        """setEmailFolder : Sets the emails folder path

        Args:
            folderpath (str): folderpath to the emails folder
        """
        if not folderpath.endswith("/"):
            folderpath += "/"
        cls.emailFolder = folderpath

    @classmethod
    def getEmailNumber(cls) -> int:
        """
        getEmailNumber : Returns the number of email adresses stored

        Returns:
            int: Number of email addresses
        """

        return len(os.listdir(cls.emailFolder))

    @classmethod
    def createMail(cls, mail: str) -> str:
        """createMail : Creates a folder for the supplied email

        Args:
            mail (str): email in the form example@domain.xxx

        Returns:
            str: folderpath to the email folder
        """
        mailPath = cls.emailFolder + mail.replace("/", " ")
        os.mkdir(mailPath)

        mailDict = {
            "email": mail,
            "photoNumber": 0,
        }
        with open(mailPath + "/email.json", "wt", encoding=ENCODING) as file:
            json.dump(mailDict, file, indent=4)

        return mailPath

    @classmethod
    def getMail(cls, mail: str) -> str:
        """getMail : Retrieves folderpath to the mail folder.

        Args:
            mail (str): email in the form example@domain.xxx

        Returns:
            str: Filepath to the email folder, empty string if not found.
        """
        mailPath = cls.emailFolder + mail.replace("/", " ")
        if not os.path.exists(mailPath):
            return ""
        return mailPath

    @classmethod
    def _readEmailInfo(cls, mail: str) -> dict:
        """_readEmailInfo : Returns email info json file as dict object.

        Args:
            mail (str):  email in the form example@domain.xxx

        Returns:
            dict: Python representation of the JSON file
        """
        with open(
            cls.emailFolder + mail + "/" + INFOFILE, "rt", encoding=ENCODING
        ) as file:
            return json.load(file)

    @classmethod
    def _writeEmailInfo(cls, infoDict: dict) -> None:
        """_writeEmailInfo _summary_

        Args:
            infoDict (dict): _description_
        """
        with open(cls.emailFolder + INFOFILE, "wt", encoding=ENCODING) as file:
            json.dump(file, infoDict)

    @classmethod
    def addPhotoToMail(cls, photoPath: str) -> None:
        """addPhotoToMail

        Args:
            photoPath (str): photo filepath to add to email
        """
        mailStr = QInputDialog.getText(
            cls,
            "Emails (séparés par des virgules)",
            "Votre ou vos emails séparés par des virgules",
        )
        mailList = [mail.strip() for mail in mailStr.split(",")]

        for mail in mailList:

            mailPath = cls.getMail(mail)
            if len(mailPath) == 0:
                mailPath = cls.createMail(mail)

            if len(photoPath) == 0:
                logger.error("No photo supplied")
                return

            shutil.copy(photoPath, mailPath)

            mailDict = cls._readEmailInfo(mail)
            mailDict["photoNumber"] += 1
            cls._writeEmailInfo(mailDict)
