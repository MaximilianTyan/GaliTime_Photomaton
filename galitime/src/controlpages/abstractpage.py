#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module defining a base page
"""

import abc
import logging

from PyQt5.QtWidgets import QMainWindow, QWidget

# ---------- LOGGER SETUP ----------
logger = logging.getLogger(__name__)
logger.propagate = True


# ----------------------------------


class AbstractPage(abc.ABC):
    """
    MailPage : Handles email sending functionality
    """

    @abc.abstractmethod
    def __init__(self, mainWindow: QMainWindow):
        self.mainWindow = mainWindow

    @abc.abstractmethod
    def load(self) -> QWidget:
        """
            load : Loads the page in a QWidget and returns it

            Returns:
                PyQt5.QtWidget: Camera page loaded layout
        """
        ...
