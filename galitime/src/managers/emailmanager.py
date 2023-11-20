#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module in charge of email handling
"""

import atexit
# Config & data files
import configparser
import email.message
import json
import logging
import mimetypes
# File manipulation
import os
import shutil
# Email sending
import smtplib

from .emailinput import EmailInput
from ..utilities.constants import EMAIL_CONFIG_FILE
from ..utilities.constants import EMAIL_INFO_FILE, ENCODING

logger = logging.getLogger(__name__)
logger.propagate = True


class EmailManager:
    """emailManager : Class responsible for managing mail storage and access"""

    eventManager = None
    config = configparser.ConfigParser()
    emailFolder = None
    mailSession: smtplib.SMTP = None

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
    def setEventManager(cls, eventManager: str) -> None:
        """setEventManager : Sets the event manager object

        Args:
            eventManager (EventManager): Reference to the event manager
        """
        if eventManager is not None:
            cls.eventManager = eventManager

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
    def getEmailList(cls) -> list[str]:
        """
        getEmailList : Returns a list contining all email folders

        Returns:
            list[str]: List of emai folders
        """
        return os.listdir(cls.emailFolder)

    @classmethod
    def createMailFolder(cls, mail: str) -> str:
        """createMailFolder : Creates a folder for the supplied email

        Args:
            mail (str): email in the form example@domain.xxx

        Returns:
            str: folderpath to the email folder
        """
        mailPath = cls.emailFolder + mail.replace("/", " ")
        os.mkdir(mailPath)

        mailDict = {
            "email": mail, "photoNumber": 0,
        }
        cls._writeEmailInfo(mail, mailDict)

        logger.info("New email folder created for email %s", mail)

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
    def readConfig(cls) -> None:
        """
        Reads the EMAIL_CONFIG_FILE if it exists and updates the internal config
        parser object accordingly
        """
        if not os.path.exists(EMAIL_CONFIG_FILE):
            logger.warning("Missing email server config file: %s", EMAIL_CONFIG_FILE)
            return
        cls.config.read(EMAIL_CONFIG_FILE)
        logger.debug("Read %s config file", EMAIL_CONFIG_FILE)

    @classmethod
    def getConfig(cls) -> configparser.ConfigParser:
        """Returns the current mail configuration as a config parser.

        Returns:
            configparser.ConfigParser: Mail config parser
        """
        return cls.config

    @classmethod
    def _readEmailInfo(cls, mail: str) -> dict:
        with open(
                cls.emailFolder + mail + "/" + EMAIL_INFO_FILE, "rt", encoding=ENCODING
        ) as file:
            return json.load(file)

    @classmethod
    def _writeEmailInfo(cls, mail: str, infoDict: dict) -> None:
        mailPath = cls.emailFolder + mail.replace("/", " ")

        with open(mailPath + "/" + EMAIL_INFO_FILE, "wt", encoding=ENCODING) as file:
            json.dump(infoDict, file, indent=4)

    @classmethod
    def addPhotoToMailFolder(cls, photoPath: str) -> None:
        """addPhotoToMailFolder

        Args:
            photoPath (str): photo filepath to add to email
        """
        Input = EmailInput()
        Input.prompt(cls.getEmailList())
        mailList = Input.getSelectedMails()

        for mail in mailList:
            mailPath = cls.getMail(mail)
            if len(mailPath) == 0:
                mailPath = cls.createMailFolder(mail)

            if len(photoPath) == 0:
                logger.error("No photo supplied")
                return

            shutil.copy(photoPath, mailPath)

            mailDict = cls._readEmailInfo(mail)
            mailDict["photoNumber"] += 1
            cls._writeEmailInfo(mail, mailDict)

        logger.info("Added photo to %s mail folders", repr(mailList))

        # cls.sendViaMail(mailList, photoPath)

    @classmethod
    def connectToMailServer(cls) -> smtplib.SMTP:
        """
        connectToMailServer : Creates and return a connection object to the mail server
        The connection parameters are configured in the email.cfg file.

        Returns:
            smtplib.SMTP: COnnection session
        """
        config = cls.getConfig()

        # port = config["server"]["port"]
        # host = config["server"]["hostname"]
        # session = smtplib.SMTP(
        #     host=host, port=port
        # )

        session = smtplib.SMTP(
            "localhost"
        )

        cls.mailSession = session
        atexit.register(cls.closeConnection)

        session.starttls()

        logger.info(
            "Opening connection to mail server " + config["server"]["hostname"] + ":" +
            config["server"]["hostname"]
        )

        # Loging in
        user = config["user"]["login"]
        keyFile = config["files"]["key_path"]

        if not os.path.exists(keyFile):
            raise FileNotFoundError(f"No {keyFile} file could be found for logging in")
        with open(
                keyFile, "rt", encoding=ENCODING
        ) as file:
            password = file.read().strip()

        session.login(user=user, password=password)

    @classmethod
    def closeConnection(cls) -> None:
        """
        closeConnection : Closes the connection to the SMTP server
        """
        try:
            cls.mailSession.close()
            logger.info("Server connection closed")
        finally:
            pass

    @classmethod
    def createMailMessage(
        cls, emailAddress: str, imagePathList: list[str]
    ) -> email.message.EmailMessage:
        """
        createMailMessage : Creates an email object and adds each image as an
        attachement.
        The mail body is configured in the email.cfg file.

        Args:
            emailAddress (str): Email addresse to send the created mail to.
            imagePathList (list(str)): List of image file to be sent with the email.

        Returns:
            email.message.EmailMessage : Mail object destined for emailAddress with
            images as attachements.
        """

        # https://learn.microsoft.com/en-us/previous-versions/office/developer
        # /exchange-server-2010/aa563064(v=exchg.140)
        # And chatGPT with "SMTP MIME Tree for HTML+embedded images+attachements"
        # Multipart / Mixed
        # | -- Multipart / Related
        # | | -- Text / HTML
        # | | -- Image(Embedded)
        # | -- Attachment

        config = cls.getConfig()

        # Email writing
        message = email.message.EmailMessage()
        message["Subject"] = config["message"]["subject"]
        message["From"] = config["message"]["from"]
        message["To"] = [emailAddress]

        # Add HTML content
        with open(config["files"]["body_path"], 'rt') as file:
            file_content = file.read()

        file_content = cls._replaceMailTemplate(file_content, emailAddress, imagePathList);
        message.add_related(file_content.encode('utf-8'), maintype='text', subtype='html')

        # Add resources used in the HTML file
        resources_path = config["files"]["resources_path"]
        if not resources_path.endswith('/'):
            resources_path += '/'

        for filename in os.listdir(resources_path):
            filepath = resources_path + filename

            mimeType, _ = mimetypes.guess_type(filepath)
            maintype, subtype = mimeType.split('/')
            with open(filepath, 'rb') as file:
                message.add_related(file.read(), maintype=maintype, subtype=subtype)

        # Attachements, here photos
        for imagePath in imagePathList:
            with open(imagePath, 'rb') as image:
                mimeType, _ = mimetypes.guess_type(imagePath)
                maintype, subtype = mimeType.split('/')
                message.add_attachment(image.read(), maintype=maintype, subtype=subtype)

        return message

    @classmethod
    def _replaceMailTemplate(
        cls,
        fileContent: str,
        emailAddr: str = None,
        photoPathList: list[str] = None
    ) -> str:
        """
        _replaceMailTemplate: Replaces template {tags} with appropriate values

        Template {tags} include:
            {event_name}
            {event_date}
            {photo_number}
            {email}
            {html_photos}

        Args:
            fileContent (str) : Template file content

        Optional args:
            emailAddr (str): Email recipient, defaults to None
            photoPathList (list[str]): Photos URL, defaults to None

        Returns:
            str: File content with {tags} replaced
        """

        if "{event_name}" in fileContent:
            fileContent = fileContent.replace(
                "{event_name}",
                cls.eventManager.getEventName()
            )

        if "{event_date}" in fileContent:
            fileContent = fileContent.replace(
                "{event_date}",
                cls.eventManager.getEventDate()
            )

        if "{photo_number}" in fileContent:
            fileContent = fileContent.replace(
                "{photo_number}",
                str(len(photoPathList))
            )

        if "{email}" in fileContent:
            if emailAddr is None:
                raise ValueError(
                    "Email wasn't provided to the template populating function"
                )
            fileContent = fileContent.replace("{email}", str(emailAddr))

        if "{html_photos}" in fileContent:
            if photoPathList is None:
                raise ValueError(
                    "Photos URL list wasn't provided to the template populating "
                    "function"
                )
            url_tag = cls.config['message']['photos_html_tag']
            html_tags = [url_tag.format(os.path.basename(url)) for url in photoPathList]
            fileContent = fileContent.replace("{html_photos}", '\n'.join(html_tags))

        print(fileContent)
        return fileContent

    @classmethod
    def sendSingleMail(cls, message: email.message.EmailMessage) -> None:
        """Send the provided email object through the SMTP connection

        Args:
            message (email.message.EmailMessage):
        """
        logger.info("Sending single mail...")
        cls.connectToMailServer()

        status = cls.mailSession.send_message(message.as_string())
        logger.info("Mail send request returned status %s", str(status))

        cls.closeConnection()

    @classmethod
    def sendPhotosToMails(cls, mailFolderList: list[str]) -> None:
        """
        Sends all photos in the email folder to relevant email

        Args:
            mailFolderList (list[str]): List of email to send named folders to
        """
        logger.info("Sending %u emails containing photos", len(mailFolderList))

        cls.connectToMailServer()

        mailsStatuses = []
        for emailFolder in mailFolderList:
            folderPath = cls.getEmailFolder() + emailFolder
            if not folderPath.endswith('/'):
                folderPath += '/'

            # Retrieve destination address
            with open(folderPath + EMAIL_INFO_FILE, "rt", encoding=ENCODING) as info:
                emailAddress = json.load(info)["email"].strip()

            imagePathList = [
                folderPath + imagePath for imagePath in os.listdir(folderPath)
            ]
            if folderPath + EMAIL_INFO_FILE in imagePathList:
                imagePathList.remove(folderPath + EMAIL_INFO_FILE)

            message = cls.createMailMessage(emailAddress, imagePathList)
            errorsDict = cls.mailSession.send_message(message)
            if len(errorsDict):
                mailsStatuses.append(errorsDict)

        if not mailsStatuses:
            logger.info("All mails have been sent")
        else:
            logger.warning(
                "%d Email send errors occured:\n%s",
                len(mailsStatuses),
                "\n".join(mailsStatuses),
            )

        cls.closeConnection()

