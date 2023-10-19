#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Control window module, contains widget declarative functions,
functionnality functions are stored in controlfunctions.py
"""

from enum import auto, Enum


class PageEnum(Enum):
    START = auto()
    OPTIONS = auto()
    CONTROL = auto()
    CAMERA = auto()
    PRINTER = auto()
    MAIL = auto()
