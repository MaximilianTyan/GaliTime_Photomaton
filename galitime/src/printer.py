#!/bin/python3
# encoding:utf-8
# coding:utf-8

"""
Module to handle printer interaction
"""

import logging
import subprocess

from .constants import PRINTER

logger = logging.getLogger(__name__)
logger.propagate = True


class ImagePrinter:
    """
    ImagePrinter : Handles printer jobs and interactions
    """

    PrinterInstance = None

    def __init__(self):
        ImagePrinter.PrinterInstance = self

    @classmethod
    def getPrinter(cls) -> object:
        """
        getPrinter : Returns the current printer instance

        Returns:
            ImagePrinter: Current printer instance
        """
        return cls.PrinterInstance

    def printImage(self, filepath: str) -> None:
        f"""
        printImage : Prints file with the printer {PRINTER} using 'lpr' command and CUPS with GutenPrint 5.3.4 drivers.
        Raises an Exception if the process returns a non zero error code.

        Args:
            filepath (str): Filepath of the image to print
        """
        if filepath is None or len(filepath) == 0:
            raise FileNotFoundError("Filepath is empty")
        
        # Clear pending jobs
        subprocess.run(["lprm", "-P", PRINTER, "-"])

        logger.info("Printing %s" % filepath)
        result = subprocess.run(["lpr", "-P", PRINTER, "-o", "media=w288h432", "-o", "StpiShrinkOutput=Expand", filepath], check=True)
        logger.info("Return of print command %s" % str(result))
