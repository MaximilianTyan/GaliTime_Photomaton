#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module to handle the event options page
"""

import logging
import smtplib
import socket

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QVBoxLayout, QWidget
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QMessageBox

from ..abstractcontrolwindow import AbstractControlWindow
from ..controlpages.abstractpage import AbstractPage
from ..controlpages.pagesenum import PageEnum
from ..managers.emailmanager import EmailManager
from ..utilities.stylesheet import cssify

# ---------- LOGGER SETUP ----------
logger = logging.getLogger(__name__)
logger.propagate = True
# ----------------------------------

NORMAL_STYLE = "background-color: rgb(250, 250, 250); color: black;"


class MailPage(AbstractPage):
    """
    MailPage : Handles email sending functionnality
    """

    def __init__(self, mainWindow: AbstractControlWindow):
        self.EmailList: QListWidget = None
        self.MailCountEdit: QLineEdit = None
        self.mainWindow = mainWindow
        self.ServerHostnameEdit = None
        self.ServerPortEdit = None
        self.LoginUsernameEdit = None

    def load(self) -> QWidget:
        """Loads the control page in a QWidget and returns it.

        Returns:
            PyQt5.QtWidget: Mail page loaded layout.
        """
        # Main layout, vertical, contains Everything
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
        MainVLayout.setContentsMargins(
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10,
            self.mainWindow.width() // 10, )
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1 Two columns container
        ColumnContainerHLayout = QHBoxLayout()
        MainVLayout.addLayout(ColumnContainerHLayout)

        # 1.1 Left column
        LeftColumnVLayout = QVBoxLayout()
        LeftColumnVLayout.setAlignment(Qt.AlignCenter)
        ColumnContainerHLayout.addLayout(LeftColumnVLayout)

        # 1.1.1 Mail count text input
        self.MailCountEdit = QLineEdit()
        self.MailCountEdit.setEnabled(False)
        self.MailCountEdit.setStyleSheet(NORMAL_STYLE)
        self.MailCountEdit.setAlignment(Qt.AlignCenter)
        self.updateMailCount()
        LeftColumnVLayout.addWidget(self.MailCountEdit)

        # 1.1.2. Email & Server config list view
        self.EmailList = QListWidget()
        self.updateMailList()
        LeftColumnVLayout.addWidget(self.EmailList)

        # 1.2 Right column
        RightColumnVLayout = QVBoxLayout()
        ColumnContainerHLayout.addLayout(RightColumnVLayout)

        # 1.2.1 Info layout
        InfoGridLayout = QGridLayout()
        InfoGridLayout.setSpacing(10)
        InfoGridLayout.setAlignment(Qt.AlignTop)
        RightColumnVLayout.addLayout(InfoGridLayout)

        # 1.2.1.0 Server config Label
        ServerConfigLabel = QLabel("Configuration du serveur")
        ServerConfigLabel.setAlignment(Qt.AlignHCenter)
        InfoGridLayout.addWidget(ServerConfigLabel, 1, 1, 1, 2)

        # 1.2.1.1 Server hostname label
        ServerHostnameLabel = QLabel("Addresse du serveur:")
        ServerHostnameLabel.setAlignment(Qt.AlignRight)
        InfoGridLayout.addWidget(ServerHostnameLabel, 2, 1)

        EmailManager.readConfig()
        # 1.2.1.2 Server hostname LineEdit
        self.ServerHostnameEdit = QLineEdit()
        self.ServerHostnameEdit.setEnabled(False)
        self.ServerHostnameEdit.setStyleSheet(NORMAL_STYLE)
        InfoGridLayout.addWidget(self.ServerHostnameEdit, 2, 2)

        # 1.2.2.1 Server port label
        ServerPortLabel = QLabel("Port du serveur:")
        ServerPortLabel.setAlignment(Qt.AlignRight)
        InfoGridLayout.addWidget(ServerPortLabel, 3, 1)

        # 1.2.2.2 Server port LineEdit
        self.ServerPortEdit = QLineEdit()
        self.ServerPortEdit.setEnabled(False)
        self.ServerPortEdit.setStyleSheet(NORMAL_STYLE)
        InfoGridLayout.addWidget(self.ServerPortEdit, 3, 2)

        # 1.2.3.1 Server port label
        LoginUsernameLabel = QLabel("Identifiant:")
        LoginUsernameLabel.setAlignment(Qt.AlignRight)
        InfoGridLayout.addWidget(LoginUsernameLabel, 4, 1)

        # 1.2.3.2 Server port LineEdit
        self.LoginUsernameEdit = QLineEdit()
        self.LoginUsernameEdit.setEnabled(False)
        self.LoginUsernameEdit.setStyleSheet(NORMAL_STYLE)
        InfoGridLayout.addWidget(self.LoginUsernameEdit, 4, 2)

        # 2. Send / Quit button layout
        SendQuitButtonsHLayout = QHBoxLayout()
        MainVLayout.addLayout(SendQuitButtonsHLayout)

        # 2.1 Send buttons
        SendButton = QPushButton("Envoyer")
        SendButton.setStyleSheet(cssify("Tall Blue"))
        SendButton.clicked.connect(self.sendPhotosToMails)
        SendQuitButtonsHLayout.addWidget(SendButton)

        # 2.2 Quit buttons
        BackButton = QPushButton("Retour")
        BackButton.setStyleSheet(cssify("Tall Red"))
        BackButton.clicked.connect(lambda: self.mainWindow.loadPage(PageEnum.CONTROL))
        SendQuitButtonsHLayout.addWidget(BackButton)

        self.readConfig()

        logger.debug("Mail page loaded")
        return MainContainer

    def updateMailCount(self) -> None:
        """Update the number of emails to be sent"""
        self.MailCountEdit.setText(
            str(EmailManager.getEmailNumber()) + " dossiers email trouvés"
        )

    def updateMailList(self) -> None:
        """Update the email list view"""
        emaiStrList = EmailManager.getEmailList()
        logger.info("Updating email list with %d entries", len(emaiStrList))

        for email in emaiStrList:
            emailItem = QListWidgetItem(email)
            emailItem.setFlags(emailItem.flags() | Qt.ItemIsUserCheckable)
            emailItem.setCheckState(Qt.Checked)
            self.EmailList.addItem(emailItem)

    def sendPhotosToMails(self) -> None:
        """
        Sends emails to selected persons
        """
        selectedEmailFolders: list[str] = [self.EmailList.item(i).text() for i in
            range(self.EmailList.count()) if
            self.EmailList.item(i).checkState() == Qt.Checked]
        logger.info("Sending %d with corresponding photos", len(selectedEmailFolders))
        try:
            EmailManager.sendPhotosToMails(selectedEmailFolders)
        except (socket.gaierror, smtplib.SMTPException) as err:
            logger.error(
                "A mail sending error occurred : %s\n", str(err)
            )
            QMessageBox.critical(
                None,
                "Sending error",
                "An mail sending error occurred while trying to send "
                f"{len(selectedEmailFolders)} mails:\n\nError:\n{err}"
            )

    def readConfig(self):
        EmailManager.readConfig()
        self.ServerHostnameEdit.setText(EmailManager.getConfigField("server/hostname"))
        self.ServerPortEdit.setText(EmailManager.getConfigField("server/port"))
        self.LoginUsernameEdit.setText(EmailManager.getConfigField("user/login"))

