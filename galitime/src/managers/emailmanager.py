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

from PyQt5.QtWidgets import QMessageBox

from .emailinput import EmailInput
from ..utilities.constants import EMAIL_CONFIG_FILE
from ..utilities.constants import EMAIL_INFO_FILE, ENCODING
from ..utilities.constants import DEFAULT_PHOTO

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
            QMessageBox.critical(
                cls.eventManager.parent,
                "Missing email configuration file",
                f"No {EMAIL_CONFIG_FILE} file found\n"
            )
            logger.warning("Missing email server config file: %s", EMAIL_CONFIG_FILE)
            return

        cls.config.read(EMAIL_CONFIG_FILE)
        logger.debug("Read %s config file", EMAIL_CONFIG_FILE)

    @classmethod
    def getConfigField(cls, path: str) -> str:
        """Returns field from the configuration, prompting an error if not found

        Args:
            path (str): Variable to get in the form 'section/value'

        Returns:
            str: Configuration value if found, None if not found
        """

        section, variable = path.split('/', 1)

        if section not in cls.config:
            error_msg = f"No '{section}' section in email config file"
        elif variable not in cls.config[section]:
            error_msg = (f"No '{variable}' value in '{section}' section in email "
                         f"config file")
        else:
            return cls.config[section][variable]
        logger.error(error_msg)
        QMessageBox.critical(cls.eventManager.parent, "Configuration error", error_msg)

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
        if os.path.basename(photoPath) == DEFAULT_PHOTO:
            logger.warning("Ignoring default photo %s", DEFAULT_PHOTO)

        Input = EmailInput()
        Input.prompt(cls.getEmailList())
        mailList = Input.getSelectedMails()

        if len(mailList) == 0:
            logger.warning("Mail destination list is empty, returning from func call")
            return

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

        logger.info("Added photo %s to %s mail folders", photoPath, repr(mailList))

        # cls.sendViaMail(mailList, photoPath)

    @classmethod
    def connectToMailServer(cls) -> smtplib.SMTP_SSL:
        """
        connectToMailServer : Creates and return a connection object to the mail server
        The connection parameters are configured in the email.cfg file.

        Returns:
            smtplib.SMTP_SSL: Connection session or None if error occured
        """
        cls.readConfig()
        hostname = cls.getConfigField("server/hostname")
        port = cls.getConfigField("server/port")
        if hostname is None or port is None:
            return

        logger.info(
            "Opening connection to mail server " + hostname + ":" +
            str(port)
        )

        try:
            session = smtplib.SMTP_SSL(
                host=hostname,
                port=int(port)
            )
        except ConnectionRefusedError:
            error_msg = "Connection has been refused by server"
            logger.error(error_msg)
            QMessageBox.critical(cls.eventManager.parent, "Server error", error_msg)
            return

        cls.mailSession = session
        atexit.register(cls.closeConnection)

        username = cls.getConfigField("user/login")
        key_file = cls.getConfigField("files/key_path")

        # Loging in
        if not os.path.exists(key_file):
            raise FileNotFoundError(f"No {key_file} file could be found for logging in")
        with open(
                key_file, "rt", encoding=ENCODING
        ) as file:
            password = file.read().strip()

        session.login(user=username, password=password)

        return session

    @classmethod
    def closeConnection(cls) -> None:
        """
        closeConnection : Closes the connection to the SMTP server
        """
        if cls.mailSession is None:
            logger.debug("Attempted to close non existant server connection, returning")
            return
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

        cls.readConfig()

        # Email writing
        message = email.message.EmailMessage()
        message["Subject"] = cls.getConfigField("message/subject")
        message["From"] = cls.getConfigField("message/from")
        message["To"] = [emailAddress]

        # Add HTML content
        with open(cls.getConfigField("files/body_path"), 'rt') as file:
            file_content = file.read()

        file_content = cls._replaceMailTemplate(
            file_content,
            emailAddress,
            imagePathList
        )
        message.add_related(
            file_content.encode('utf-8'),
            maintype='text',
            subtype='html'
        )

        # Add resources used in the HTML file
        resources_path = cls.getConfigField("files/resources_path")
        if not resources_path.endswith('/'):
            resources_path += '/'

        for filename in os.listdir(resources_path):
            filepath = resources_path + filename

            mimeType, _ = mimetypes.guess_type(filepath)
            maintype, subtype = mimeType.split('/')
            cid = cls._getCIDfromFile(filename)

            with open(filepath, 'rb') as file:
                message.add_related(
                    file.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename,
                    cid=cid
                )

        # Attachements, here photos
        for imagePath in imagePathList:
            with open(imagePath, 'rb') as image:
                mimeType, _ = mimetypes.guess_type(imagePath)
                maintype, subtype = mimeType.split('/')
                filename = os.path.basename(imagePath)
                cid = cls._getCIDfromFile(filename)
                message.add_attachment(
                    image.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename,
                    cid=cid
                )

        return message

    @classmethod
    def _getCIDfromFile(cls, filename: str) -> str:
        """_getCIDfromFile: Generates an email Content ID from a filename

        Args:
            filename (str): filename to convert into a cid

        Returns:
            str: Generated Content ID from filename
        """
        cid = ""
        for char in filename:
            if char.isalpha():
                cid += char
            else:
                cid += '_'
        return cid

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
            url_tag = cls.getConfigField("message/photos_html_tag")

            html_tags = []
            for photoPath in photoPathList[:3]:
                inlineFilename = cls._getCIDfromFile(os.path.basename(photoPath))
                html_tags.append(url_tag.format('cid:' + inlineFilename))

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
        if cls.connectToMailServer() is None:
            logger.error("Failed to establish connection to mail server, returning")
            return

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

        if cls.connectToMailServer() is None:
            logger.error("Failed to establish connection to mail server, returning")
            return

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
            print(message.as_string())
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
