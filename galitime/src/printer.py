#!/bin/python3
# encoding:utf-8
# coding:utf-8

"""
Module to handle printer interaction
"""

import logging
import subprocess

from constants import PRINTER

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

    def printImage(self, filepath):
        result = subprocess.run(["lpr", filepath, "-P", PRINTER], check=True)
        logger.info("Return code for print command %u", result)
