#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module for email handling
"""

# File manipulation
import os
import shutil

# Config & data files
import json
import configparser

# Email sending
import smtplib
import email
import mimetypes
import datetime

import atexit
import logging

from PyQt5.QtWidgets import QInputDialog

from ..constants import ENCODING, INFO_FILE, DATE_FORMAT

logger = logging.getLogger(__name__)
logger.propagate = True


class EmailManager:
    """emailManager : Class responsible for managing mail storage and access"""

    emailFolder = None
    mailSession = None

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
    def getEmailFolder(cls) -> str:
        """
        getEmailFolder : Returns the email folder path

        Returns:
            str: Email folder path
        """
        return cls.emailFolder

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
            cls.emailFolder + mail + "/" + INFO_FILE, "rt", encoding=ENCODING
        ) as file:
            return json.load(file)

    @classmethod
    def _writeEmailInfo(cls, infoDict: dict) -> None:
        """_writeEmailInfo _summary_

        Args:
            infoDict (dict): _description_
        """
        with open(cls.emailFolder + INFO_FILE, "wt", encoding=ENCODING) as file:
            json.dump(file, infoDict)

    @classmethod
    def addPhotoToMailFolder(cls, photoPath: str) -> None:
        """addPhotoToMailFolder

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
        
        #cls.sendViaMail(mailList, photoPath)
    
    @classmethod
    def connectToMailServer(cls) -> smtplib.SMTP:
        """
        connectToMailServer : Creates and return a connection object to the mail server
        The connection parameters are configured in the email.cfg file.

        Returns:
            smtplib.SMTP: COnnection session
        """
        config = configparser.ConfigParser()
        config.read("./email.cfg")


        session = smtplib.SMTP(
            host=config["server"]["hostname"],
            port=config["server"]["port"]
        )

        cls.mailSession = session
        atexit.register(cls.closeConnection)

        session.starttls()

        logger.info("Opening connection to mail server %s" % config["server"]["hostname"] + ':' + config["server"]["hostname"])

        # Loging in
        user = config["user"]["login"]
        with open("./email.key", "rt", encoding=ENCODING) as file:  # The filepath is hardcoded to avoid forgetting to add it in gitignore
            password = file.read().strip()

        session.login(user=user, password=password)


    @classmethod
    def closeConnection(cls):
        try:
            cls.mailSession.close()
            logger.info("Connection closed")
        finally: pass


    @classmethod
    def createMail(cls, emailAddress: str, imagePathList:list[str]) -> email.message.EmailMessage:
        """
        createMail : Creates an email object and adds each image as an attachement.
        The mail body is configured in the email.cfg file.

        Args:
            emailAddress (str): Email addresse to send the created mail to.
            imagePathList (list(str)): List of image file to be sent with the email.
        
        Returns:
            email.message.EmailMessage : Mail object destined for emailAddress with images as attachements.
        """

        # Email writing
        message = email.message.EmailMessage()
        message["Subject"] = config["message"]["body"].format(date=datetime.date().strftime(DATE_FORMAT))
        message["From"] = user
        message["To"] = emailAddress

        for imagePath in imagePathList:
            ctype, fileEncoding = mimetypes.guess_type(imagePath)
            subtype = ctype.split('/')[1]

            with open(imagePath, 'rb', encoding=fileEncoding) as file:
                imgData = file.read()
            message.add_attachment(imgData, maintype="image", subtype=subtype)
        
        return message
    
    @classmethod
    def sendSingleMail(cls, mail):
        logger.info("Sending single mail...")
        cls.connectToMailServer()

        status = cls.mailSession.send_message(message)
        logger.info("Mail send request returned status %s" + str(status))

        cls.closeConnection()
        

    @classmethod
    def sendAllPhotosToMails(cls):
        mailFolderList = os.listdir(self.getEmailFolder())
        logger.info("Sending %u emails containing photos" % len(mailFolderList))
        
        cls.connectToMailServer()

        for emailFolder in mailFolderList:
            with open(emailFolder + INFO_FILE, 'rt', encoding=ENCODING) as info:
                emailAddress = info.read().strip()
            
            os.listdir(emailFolder)

            message = cls.createMail(emailAddress, imagePathList)

            satus = cls.mailSession.send_message(message)
        
        logger.info("All mails have been sent")

        cls.closeConnection()  

       
