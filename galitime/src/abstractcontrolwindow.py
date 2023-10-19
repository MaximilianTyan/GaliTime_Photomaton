#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Control window module, contains widget declarative functions,
functionnality functions are stored in controlfunctions.py
"""
from __future__ import annotations

import abc
import enum
import logging

from PyQt5.QtWidgets import QMainWindow

# ---------- LOGGER SETUP ----------
logger = logging.getLogger(__name__)
logger.propagate = True


# ----------------------------------

class AbstractControlWindow(QMainWindow):
    """ControlWindow : Main control window holding buttons, labels and every control widget"""

    @classmethod
    @abc.abstractmethod
    def getWindow(cls) -> AbstractControlWindow:
        """
        getWindow : Returns the control window instance

        Returns:
            QMainWindow: Control window instance
        """
        ...

    @abc.abstractmethod
    def loadPage(self, page: enum.Enum, *args, **kwargs) -> None:
        """
        loadPage : Loads and displays the requested page

        Args:
            page (str): page name
        """
        ...

    @abc.abstractmethod
    def toggleFullscreen(self) -> None:
        """
        toggleFullscreen : Toggles fullscreen/windowed view
        """
        ...
