#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module containing class handling camera IO and related functions
"""

import os
import subprocess
import time
import logging
import atexit
import psutil

import gphoto2 as gp
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime

logger = logging.getLogger(__name__)
logger.propagate = True

ENCODING = "utf-8"
MOVIEPATH = "movie.mjpg"

STARTBYTES = b"\xFF\xD8\xFF"
STOPBYTES = b"\xFF\xD9"


def popError(func) -> callable:
    """
    popError : Decorator aimed at encapsulating a function call in a try/except
    structure and prompt any error into a popup. This aims at informing about 
    camera error (the most common) without having to restart the whole application.

    Args:
        func (callable): function to encapsulate

    Returns:
        callable: encapsulated function with error prompt handler
    """

    def handled(*args, **kwargs):
        try:
            retval = func(*args, **kwargs)
        except Exception as err:
            logger.error("A camera error occured in function : %s : %s", func, err)
            QMessageBox.critical(
                None, "Camera error", f"An error occured in function \n{func}:\n {err}"
            )
            return None
        return retval

    # ---
    return handled


class CameraWrapper:
    """
    Wrapper class for the camera, in charge of creating and managing processes 
    responsible for previewing images.
    """

    def __init__(self) -> None:

        self.isPreviewing = False
        self.previewProcess = None

        self.prevFileSize = 0
        self.prevFrame = b""
        self.previewStartTime = 0

        self.frameCount = 0

        self._clearGphoto()

        self.cam = gp.Camera()

        self.logfile = open("logs/camera.log", "wt", encoding=ENCODING)

        # Ensuring proper cleanup
        atexit.register(self._cleanUp)

    def _clearGphoto(self) -> None:
        """
        _clearGphoto : Clear all processes origiating from gphoto2 that may lock the camera.
        """
        clearedProcess = False
        pythonPID = os.getpid()
        for process in psutil.process_iter():

            if process.pid == pythonPID:
                continue  # Don't kill current process

            if "psutil" in process.name():
                continue  # Don't kill the generator

            if "gphoto2" in process.name():
                logger.info("Killing %s", process)
                try:
                    process.kill()
                    clearedProcess = True
                except psutil.AccessDenied:
                    logger.warning("Failed to kill %s", process)

        if not clearedProcess:
            logger.info("No process cleared")

    def _cleanMovieFile(self) -> None:
        filesize = os.path.getsize(MOVIEPATH)
        with open(MOVIEPATH, "wt", encoding=ENCODING) as file:
            file.write("")
        logger.info("Cleared %s file (%u bytes)", MOVIEPATH, filesize)

    @popError
    def connect(self) -> None:
        """
        connect : Initiates connection to camera device
        """
        self.cam.init()

    @popError
    def listCams(self) -> tuple:
        """
        listCams : Get available cameras

        Returns:
            tuple: Tuple containing available camera list
        """
        return tuple(gp.Camera.autodetect())

    @popError
    def takePhoto(self, saveFolder: str) -> str:
        """
        takePhoto : Trigger a photo capture

        Args:
            saveFolder (str): Folderpath where the photo taken will be placed with a
            time stamp name of format:
            "dd:MM:yyyy_hh'h'MM'm'ss's'zzz"

        Returns:
            str: photo filepath
        """
        photoPath = self.cam.capture(gp.GP_CAPTURE_IMAGE)
        photoFile = self.cam.file_get(
            photoPath.folder, photoPath.name, gp.GP_FILE_TYPE_NORMAL
        )

        timestamp = QDateTime.currentDateTime().toString(
            "dd:MM:yyyy_hh'h'MM'm'ss's'zzz"
        )
        filepath = f"{saveFolder}/{timestamp}.jpeg"

        photoFile.save(filepath)
        return filepath

    def readPreview(self) -> bytes:
        """
        readPreview : Read last available preview frame from the movie file and returns it.

        Returns:
            bytes: Last available jpeg frame
        """
        filesize = os.path.getsize(MOVIEPATH)
        if filesize == self.prevFileSize:
            return self.prevFrame
        self.prevFileSize = filesize

        self.frameCount += 1

        maxsize = 960 * 640 * 3  # Fully uncompressed image (theoretical maximum)
        with open(MOVIEPATH, "br") as file:
            # Sets cursor 690*640*3 bytes before the end of the file if possible
            file.seek(filesize - maxsize if (filesize - maxsize) > 0 else 0)
            rawdata = file.read(maxsize if maxsize < filesize else filesize)

        frame = rawdata[rawdata.rfind(STARTBYTES) :]

        if not frame.endswith(STOPBYTES):
            return self.prevFrame

        self.prevFrame = frame

        # logger.debug(f"Updating screen {len(frame)}")
        return frame

    @popError
    def startPreview(self) -> None:
        """
        startPreview : Starts seperate process for capturing preview,
        releases camera lock to the process.
        """
        self.cam.exit()
        self.isPreviewing = True

        self._cleanMovieFile()

        self.previewProcess = subprocess.Popen(
            ["gphoto2", "--capture-movie", "--force-overwrite"],
            stderr=subprocess.STDOUT,
            stdout=self.logfile,
        )
        # , "--stdout", "|",
        # "ffmpeg", "-i", "-", "-f", "mjpeg", "out.avi", "-y"])
        logger.info("POPEN Liveview capture started")

    @popError
    def stopPreview(self) -> None:
        """
        stopPreview : Terminates the separate preview process, stopping preview.
        Reconnects the camera for normal photo operation.
        """
        if self.isPreviewing:
            self.previewProcess.terminate()
            self.previewProcess.wait()
        self.isPreviewing = False
        logger.info("POPEN Liveview capture stopped")

        fps = round(self.frameCount / (time.time_ns() - self.previewStartTime), 3)
        logger.info("Mean FPS since last clip: %f", fps)

    def _closeLog(self) -> None:
        self.logfile.close()

    def _cleanUp(self) -> None:
        self.cam.exit()
        self.stopPreview()
        self._closeLog()

    @popError
    def getAbilities(self):
        return tuple(self.cam.get_abilities())

    @popError
    def getAbout(self):
        return self.cam.get_about()

    @popError
    def getConfig(self):
        return self.cam.get_config()

    @popError
    def getManual(self):
        return self.cam.get_manual()

    @popError
    def getPortInfo(self):
        return self.cam.get_port_info()

    @popError
    def getSimpleConfig(self):
        return self.cam.get_simple_config()

    @popError
    def getStorageInfo(self):
        return self.cam.get_storageinfo()

    @popError
    def getSummary(self):
        return self.cam.get_summary()

    @popError
    def listConfig(self):
        return self.cam.list_config()


if __name__ == "__main__":
    cam = CameraWrapper()
