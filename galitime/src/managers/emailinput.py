#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module in charge of email input
"""

import logging
import re

from PyQt5.QtWidgets import QCompleter, QLineEdit
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QLabel, QPushButton
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from ..utilities.stylesheet import cssify

logger = logging.getLogger(__name__)
logger.propagate = True

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

class EmailInput(QDialog):
    """
    EmailInput : Custom email input dialog
    """

    def __init__(self):
        QDialog.__init__(self)
        self.emailList: list[str] = []

        self.TextInput = None
        self.ListView: QListWidget = None
        self.ErrorLabel: QLabel = None

    def prompt(self, emailList) -> None:
        """
        exec : Displays the email input dialog populated with the given email addresses

        Args:
            emailList (list[str]): List of all given email addresses
        """

        MainVLayout = QVBoxLayout()
        self.setWindowTitle("Email input")

        # 1. Input Label
        InputLabel = QLabel("Adresse mail à ajouter")
        MainVLayout.addWidget(InputLabel)

        # 2. Input layout
        InputHLayout = QHBoxLayout()
        MainVLayout.addLayout(InputHLayout)

        # 2.1 Text input
        self.TextInput = QLineEdit()
        self.TextInput.setPlaceholderText("Email")
        InputHLayout.addWidget(self.TextInput)

        # 2.2 Add button
        AddButton = QPushButton("Ajouter")
        AddButton.clicked.connect(self._processInput)
        InputHLayout.addWidget(AddButton)

        completer = QCompleter(emailList)
        self.TextInput.setCompleter(completer)

        # 3. Error Label
        self.ErrorLabel = QLabel("")
        self.ErrorLabel.setStyleSheet("color: red")
        MainVLayout.addWidget(self.ErrorLabel)

        # 3. List Label
        ListLabel = QLabel("Destinataires")
        MainVLayout.addWidget(ListLabel)

        # 4. List Widget
        self.ListView = QListWidget()
        MainVLayout.addWidget(self.ListView)

        # 5. Actions button layout
        ButtonsHLayout = QHBoxLayout()
        MainVLayout.addLayout(ButtonsHLayout)

        # 5.1 Delete button
        DeleteButton = QPushButton("Supprimer")
        DeleteButton.setStyleSheet(cssify("red"))
        DeleteButton.clicked.connect(self._removeItem)
        ButtonsHLayout.addWidget(DeleteButton)

        # 5.2 Validate button
        ValidateButton = QPushButton("Valider")
        ValidateButton.clicked.connect(self.accept)
        ButtonsHLayout.addWidget(ValidateButton)

        self.setLayout(MainVLayout)

        logger.debug("Email prompt opened")
        super().exec()

    def _processInput(self) -> None:
        email = self.TextInput.text()
        self.addEmail(email)
        self.TextInput.clear()

    def _removeItem(self) -> None:
        item = self.ListView.currentItem()

        if item is None:
            logger.debug("Tried deleting unselectionned item, ignoring")
            return

        if item.text() in self.emailList:
            self.emailList.remove(item.text())

        logger.info("Removed email address %s from destinator list", item.text())

        self._updateList()

    def _updateList(self) -> None:
        self.ListView.clear()
        for email in self.emailList:
            EmailItem = QListWidgetItem(email)
            self.ListView.insertItem(0, EmailItem)

    def addEmail(self, email: str) -> None:
        """
        addEmail : Adds email in the item list

        Args:
            email (str): Email to add
        """
        _email = str(email).strip()

        if not EMAIL_REGEX.match(email):
            logger.error("Invalid email address %s", repr(_email))
            self.ErrorLabel.setText("Email non valide")
            return
        self.ErrorLabel.setText("")

        self.emailList.append(_email)
        self._updateList()
        logger.info("Added destinator %s", _email)

    def getSelectedMails(self) -> list[str]:
        """
        getSelectedMails : Returns the list of added emails

        Returns:
            list[str]: added emails list
        """
        return self.emailList


if __name__ == "__main__":
    from PyQt5.Qt import QApplication

    app = QApplication([])
    dialog = EmailInput()
    dialog.prompt(["test@example.com", "help@existence.fr"])

    app.exec()
