#!/bin/python3
# encoding:utf-8
# coding:utf-8

"""
Module to handle printer interaction
"""

import logging
import subprocess

from ..utilities.constants import PRINTER

logger = logging.getLogger(__name__)
logger.propagate = True


class ImagePrinter:
    """
    ImagePrinter : Handles printer jobs and interactions
    """

    @classmethod
    def printImage(cls, filepath: str) -> None:
        """
        printImage : Prints file with the printer defined in constants.py using 'lpr' command and CUPS with GutenPrint 5.3.4 drivers.
        Raises an Exception if the process returns a non zero error code.

        Args:
            filepath (str): Filepath of the image to print
        """
        if filepath is None or len(filepath) == 0:
            raise FileNotFoundError("Filepath is empty")

        # Clear pending jobs
        subprocess.run(["lprm", "-P", PRINTER, "-"], check=False)

        logger.info("Printing %s", filepath)
        result = subprocess.run(
            [
                "lpr",
                "-P",
                PRINTER,
                "-o",
                "media=w288h432",
                "-o",
                "StpiShrinkOutput=Expand",
                filepath,
            ],
            check=True,
        )
        logger.info("Return of print command %s", str(result))
