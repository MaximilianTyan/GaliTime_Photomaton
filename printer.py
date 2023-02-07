#!/bin/python3
# encoding:utf-8
# coding:utf-8

import logging
import subprocess

logger = logging.getLogger(__name__)
logger.propagate = True


class ImagePrinter:
    def __init__(self):
        pass

    def printImage(self, filepath):
        result = subprocess.run(["lp", filepath, "-o=4"], check=True)
        logger.info("Return code for print command %u", result)
