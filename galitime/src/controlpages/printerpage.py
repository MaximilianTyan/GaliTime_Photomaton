#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module managing the printer page
"""

import logging

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QComboBox, QHeaderView
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem

from PyQt5.QtCore import Qt

from ..peripherals.printer import ImagePrinter, PrinterError

logger = logging.getLogger(__name__)
logger.propagate = True


class PrinterPage:
    """
    StartPage : Handles printer page functionnality
    """

    def __init__(self, mainWindow):
        self.mainWindow = mainWindow

        self.PrinterChoiceBox = None
        self.PrintJobsList = None
        self.PrinterOptionsTable = None
        self.PrinterJobsTable = None

    def load(self) -> QWidget:
        """
        load : Loads the printer page in a QWidget and returns it

        Returns:
            PyQt5.QtWidget: Printer page loaded layout
        """
        logger.debug("Loading control page")
        # Main layout, vertical, contains Everything
        MainContainer = QWidget(self.mainWindow)
        MainVLayout = QVBoxLayout()
        MainVLayout.setAlignment(Qt.AlignCenter)
        MainContainer.setLayout(MainVLayout)

        # 1 Current printer layout
        CurrentPrinterHLayout = QHBoxLayout()
        MainVLayout.addLayout(CurrentPrinterHLayout)

        # 1.1 Printer label
        CurrentPrinterLabel = QLabel("Imprimante sélectionnée")
        CurrentPrinterLabel.setAlignment(Qt.AlignCenter)
        CurrentPrinterLabel.setStyleSheet("font-size: 30px")
        CurrentPrinterHLayout.addWidget(CurrentPrinterLabel)

        # 1.2 Choice box listing items
        self.PrinterChoiceBox = QComboBox()
        self.updatePrintersList()
        self.PrinterChoiceBox.currentIndexChanged.connect(self.updatePrinterOptions)
        CurrentPrinterHLayout.addWidget(self.PrinterChoiceBox)

        # 2. Two columns layout
        TwoColumnsHLayout = QHBoxLayout()
        MainVLayout.addLayout(TwoColumnsHLayout)

        # 2.1 Printer options layout
        PrinterOptionsVLayout = QVBoxLayout()
        TwoColumnsHLayout.addLayout(PrinterOptionsVLayout)

        # 2.1.1 Printer Options Label
        PrinterOptionsLabel = QLabel("Printer options")
        PrinterOptionsLabel.setAlignment(Qt.AlignCenter)
        PrinterOptionsLabel.setStyleSheet("font-size: 30px")
        PrinterOptionsVLayout.addWidget(CurrentPrinterLabel)

        # 2.1.2 Printer Options Table
        self.PrinterOptionsTable = QTableWidget()
        self.PrinterOptionsTable.setColumnCount(2)
        self.PrinterOptionsTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        PrinterOptionsVLayout.addWidget(self.PrinterOptionsTable)
        self.updatePrinterOptions()

        # 2.2 Jobs layout
        JobsVLayout = QVBoxLayout()
        TwoColumnsHLayout.addLayout(JobsVLayout)

        # 2.2.1 Jobs Label
        JobsLabel = QLabel("Impressions en cours")
        JobsLabel.setAlignment(Qt.AlignCenter)
        JobsLabel.setStyleSheet("font-size: 30px")
        JobsVLayout.addWidget(JobsLabel)

        # 2.2.2 Jobs List
        self.PrinterJobsTable = QTableWidget()
        self.PrinterJobsTable.setColumnCount(2)
        self.PrinterJobsTable.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.updatePrinterJobs()
        JobsVLayout.addWidget(self.PrinterJobsTable)

        return MainContainer

    def updatePrintersList(self) -> None:
        """
        updatePrintersList : Updates the PrinterChoiceBox widget with available printers
        """
        printerList = ImagePrinter.listPrinters()

        if printerList is None or len(printerList) == 0:
            self.PrinterChoiceBox.addItem("None")

        for printerName in printerList:
            self.PrinterChoiceBox.addItem(str(printerName))

    def updatePrinterOptions(self) -> None:
        """
        updatePrinterOptions : Updates the printer option table with options from selected printer
        """
        try:
            printerOptions = ImagePrinter.getPrinterOptions(
                self.PrinterChoiceBox.currentText()
            )
        except PrinterError:
            printerOptions = {}

        logger.debug(
            "Updating printer option table with %d entries", len(printerOptions)
        )

        self.PrinterOptionsTable.clear()
        self.PrinterOptionsTable.setRowCount(len(printerOptions))

        self.PrinterOptionsTable.setHorizontalHeaderLabels(["Option", "Valeur"])
        for row, (name, value) in enumerate(printerOptions.items()):
            optionEntry = QTableWidgetItem(name)
            self.PrinterOptionsTable.setItem(row, 0, optionEntry)

            optionValueEntry = QTableWidgetItem(value)
            self.PrinterOptionsTable.setItem(row, 1, optionValueEntry)

    def updatePrinterJobs(self) -> None:
        """
        updatePrinterJobs : Updates the jobs table with current printer jobs
        """
        jobsList = ImagePrinter.listJobs()
        logger.debug("Updating jobs table with %d entries", len(jobsList))

        # Only way to clear the table
        self.PrinterJobsTable.clear()
        self.PrinterJobsTable.setRowCount(len(jobsList))

        self.PrinterJobsTable.setHorizontalHeaderLabels(["Jobs", "Details"])
        for row, (name, value) in enumerate(jobsList.items()):
            optionEntry = QTableWidgetItem(name)
            self.PrinterJobsTable.setItem(row, 0, optionEntry)

            optionValueEntry = QTableWidgetItem(value)
            self.PrinterJobsTable.setItem(row, 1, optionValueEntry)
