#!/bin/env python3
# coding:utf-8
# encoding:utf-8

"""
Module in charge of email input
"""

import logging

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QDialog
from PyQt5.QtWidgets import QLineEdit, QCompleter
from PyQt5.QtWidgets import QListWidget, QListWidgetItem
from PyQt5.QtWidgets import QPushButton, QLabel

from ..utilities.stylesheet import cssify

logger = logging.getLogger(__name__)
logger.propagate = True


class EmailInput(QDialog):
    """
    EmailInput : Custom email input dialog
    """

    def __init__(self):
        QDialog.__init__(self)
        self.emailList = []

        self.TextInput = None
        self.ListView = None

    def prompt(self, emailList) -> None:
        """
        exec : Displays the email input dialog populated with the given email addresses

        Args:
            emailList (list[str]): List of all given email addresses
        """
        logging.debug("Opening email prompt")

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

        logging.debug("Email prompt opened")
        super().exec()

    def _processInput(self) -> None:
        email = self.TextInput.text()
        self.addEmail(email)
        self.TextInput.clear()

    def _removeItem(self) -> None:
        item = self.ListView.currentItem()

        self.ListView.removeItemWidget(self.ListView.currentItem())
        print(self.ListView.selectedItems())
        self.emailList.remove(item.text())

        logging.info("Removed email address %s from destinator list", item.text())

    def addEmail(self, email: str) -> None:
        """
        addEmail : Adds email in the item list

        Args:
            email (str): Email to add
        """
        _email = str(email).strip()

        EmailItem = QListWidgetItem(_email)

        self.ListView.insertItem(0, EmailItem)
        self.emailList.append(_email)
        logging.info("Added destinator %s", _email)

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
