#!/bin/python3
# encoding:utf-8
# coding:utf-8

"""
Module to handle printer interaction
"""

import logging
import subprocess
import os.path

import cups

from ..utilities.constants import PRINTER

logger = logging.getLogger(__name__)
logger.propagate = True


class Connection(cups.Connection):
    """
    cups.Connection wrapper adding support for 'with' keyword
    """
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self


class PrinterError(Exception):
    """
    PrinterError : Base class for printer errors
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ImagePrinter:
    """
    ImagePrinter : Handles printer jobs and interactions
    """

    printOptions = {"media": "w288h432", "StpiShrinkOutput": "Expand"}
    printerName = PRINTER

    @classmethod
    def setPrinter(cls, printerName: str):
        """
        setPrinter : Changes the selected printer for the print actions

        Raises:
            PrinterError: If the printer name doesn't match any available printers
        """
        if printerName not in cls.listPrinters():
            raise PrinterError(f"Printer {printerName} not found")
        logger.info("Changing printer name to %s", printerName)
        cls.printerName = printerName

    @classmethod
    def printImage(cls, filepath: str) -> None:
        """
        printImage : Prints file with the printer defined in constants.py using 'lpr' command and CUPS with GutenPrint 5.3.4 drivers.

        Args:
            filepath (str): Filepath of the image to print

        Raises:
            FileNotFoundError: Filepath wasn't found
        """
        if filepath is None or len(filepath) == 0:
            raise FileNotFoundError("Image filepath is empty")

        if not os.path.exists(filepath):
            raise FileNotFoundError("Image file not found")

        try:
            cls.clearJobs()
        except PrinterError as err:
            logger.warning("A printer error has occured during job cleaning: %s", str(err))

        with Connection() as cupsCon:
            cupsCon.printFile(
                cls.printerName, filepath, os.path.dirname(filepath), cls.printOptions
            )

    @classmethod
    def listPrinters(cls) -> tuple[str]:
        """
        listPrinters : Returns a tuple containing the names of available printers using pycups

        Returns:
            tuple[str]: Names of available printers
        """
        # rawEntries = subprocess.check_output(["lpstat", "-v"])
        logger.info("Querying available printers list")

        with Connection() as cupsCon:
            printersDict = cupsCon.getPrinters()

        logger.debug("Available printers: %s", str(list(printersDict.keys())))
        return tuple(printersDict.keys())

    @classmethod
    def listJobs(cls) -> dict:
        """
        listJobs : Returns a dict containing the current active jobs information


        Returns:
            dict: Jobs information stored in a dict
        """

        logger.info("Querying jobs list")

        with Connection() as cupsCon:
            jobsDict = cupsCon.getJobs()

        logger.debug("Fetched jobs: %d", len(jobsDict))
        return jobsDict

    @classmethod
    def clearJobs(cls) -> None:
        """
        clearJobs : Clears all current jobs using pycups

        Raises:
            PrinterError: If the selected printer doesn't match any available printers name
        """
        logger.debug("Clearing all jobs for printer %s", cls.printerName)

        if cls.printerName not in cls.listPrinters():
            raise PrinterError("Printer %s not found", cls.printerName)

        with Connection() as cupsCon:
            cupsCon.cancelAllJobs(cls.printerName)

        logger.info("All printing jobs cleared")

    @classmethod
    def getPrinterOptions(cls, printerName: str = None) -> dict[str, str]:
        """
        getPrinterOptions : Returns a dict containing current printer options using a call to 'lpoptions -l'
                            The class attribute printerName will be used to specify the printer using '-p'

        Raises:
            PrinterError: If the printer name doesn't match any available printers

        Returns:
            dict[str, str]: Current printer options
        """
        optionsDict = {}

        if printerName is None:
            printerName = cls.printerName
        logger.info("Querying options for printer %s", printerName)

        if printerName not in cls.listPrinters():
            raise PrinterError("Printer %s not found", cls.printerName)

        stdoutput = subprocess.check_output(
            ["lpoptions", "-p", printerName, "-l"]
        ).decode()

        for optionItem in stdoutput.split("\n"):
            if len(optionItem.strip()) == 0:
                continue
            if ":" in optionItem:
                optionName, optionValue = optionItem.split(":")

            optionsDict[optionName] = optionValue

        logging.debug("Got %d options for printer %s", len(optionsDict), printerName)
        return optionsDict
