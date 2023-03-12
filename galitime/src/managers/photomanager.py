#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Screen window, contains screen class and control options
"""

import logging

logger = logging.getLogger(__name__)
logger.propagate = True


class PhotoManager:
    """
    PhotoManager : Handles photo statistics
    """

    decorFile = None
    photoNumber = 0

    @classmethod
    def incrementPhotoNumber(cls, increment: int = 1):
        """
        incrementPhotoNumber : Increments the photo number by the given value

        Args:
            increment (int, optional): Increment value. Defaults to 1.
        """
        cls.photoNumber += increment

    @classmethod
    def getPhotoNumber(cls) -> int:
        """
        getPhotoNumber : Returns the current number of photo taken

        Returns:
            int: Number of photos
        """
        return cls.photoNumber
