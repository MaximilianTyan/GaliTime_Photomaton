#!/bin/env python3
# encoding:utf-8
# coding:utf-8

"""
Module containing class handling camera IO and related functions
"""

import os
import shutil
import subprocess
import time
import logging
import atexit

import gphoto2 as gp
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime

from .constants import ENCODING, MOVIE_PATH
from .constants import CAMERA_LOGFILE, DEFAULT_PHOTO
from .constants import START_BYTES, STOP_BYTES

logger = logging.getLogger(__name__)
logger.propagate = True

def promptError(func) -> callable:
    """
    promptError : Decorator aimed at encapsulating a function call in a try/except
    structure and prompt any error into a popup. This aims at informing about
    camera error (the most common) without having to restart the whole application.

    Args:
        func (callable): function to be encapsulated

    Returns:
        callable: encapsulated function with error prompt handler
    """

    def encapsulated(*args, **kwargs):
        # Encapsulating function
        try:
            # The function to run
            normalReturn = func(*args, **kwargs)
            return normalReturn
        except Exception as err:
            logger.error("A camera error occured in function : %s : %s", func, err)
            QMessageBox.critical(
                None, "Camera error", f"An error occured in function \n{func}:\n {err}"
            )
            return None

    return encapsulated

class CameraWrapper:
    """
    Wrapper class for the camera, in charge of creating and managing processes
    responsible for previewing images.
    """

    def __init__(self) -> None:
        self.connected = False
        self.isPreviewing = False
        self.previewProcess = None

        self.prevFileSize = 0
        self.prevFrame = b""
        self.previewStartTime = 0

        self.frameCount = 0
        self.logfile = open(CAMERA_LOGFILE, "wt", encoding=ENCODING)

        self._clearGphoto()
        self.cam = gp.Camera()

        CameraWrapper.CameraInstance = self

        if os.path.exists(MOVIE_PATH):
            os.remove(MOVIE_PATH)
        with open(MOVIE_PATH, "wb") as file:
            file.write(b"")

        # Ensuring proper cleanup
        atexit.register(self._cleanUp)

    @classmethod
    def getCamera(cls) -> object:
        """
        getCamera : Returns the current camera instance

        Returns:
            CameraWrapper: Current camera instance
        """
        return cls.CameraInstance

    def _clearGphoto(self) -> None:
        """
        _clearGphoto : Clear all processes origiating from gphoto2 that may lock the camera.
        """

        subprocess.run(["pkill", "gphoto2"])

        # clearedProcess = False
        # pythonPID = os.getpid()
        # for process in psutil.process_iter():
        #     if process.pid == pythonPID:
        #         continue  # Don't kill current process

        #     if "psutil" in process.name():
        #         continue  # Don't kill the generator

        #     if "gphoto2" in process.name():
        #         logger.info("Killing %s", process)
        #         try:
        #             process.kill()
        #             clearedProcess = True
        #         except psutil.AccessDenied:
        #             logger.warning("Failed to kill %s", process)

        # if not clearedProcess:
        #     logger.info("No process cleared")

    def _cleanMovieFile(self) -> None:
        filesize = os.path.getsize(MOVIE_PATH)
        with open(MOVIE_PATH, "wt", encoding=ENCODING) as file:
            file.write("")
        logger.info("Cleared %s file (%u bytes)", MOVIE_PATH, filesize)

    def isConnected(self) -> bool:
        return self.connected

    @promptError
    def connect(self) -> None:
        """
        connect : Initiates connection to camera device
        """
        self.connected = False
        self.cam.init()
        self.connected = True

    @promptError
    def listCams(self) -> tuple:
        """
        listCams : Get available cameras

        Returns:
            tuple: Tuple containing available camera list
        """
        return tuple(gp.Camera.autodetect())

    @promptError
    def takePhoto(self, saveFolder: str) -> str:
        """
        takePhoto : Trigger a photo capture

        Args:
            saveFolder (str): Folderpath where the photo taken will be placed with a
            time stamp name of format:
            "dd:MM:yyyy_hh'h'MM'm'ss's'zzz"

        Returns:
            str: full photo filepath
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
        filesize = os.path.getsize(MOVIE_PATH)

        if filesize == 0:
            with open(DEFAULT_PHOTO, "br") as file:
                return file.read()

        if filesize == self.prevFileSize:
            return self.prevFrame
        self.prevFileSize = filesize

        self.frameCount += 1

        # Fully uncompressed image (theoretical maximum)
        maxsize = 960 * 640 * 3 

        with open(MOVIE_PATH, "br") as file:
            # Sets cursor 690*640*3 bytes before the end of the file if possible
            file.seek(filesize - maxsize if (filesize - maxsize) > 0 else 0)
            rawdata = file.read(maxsize if maxsize < filesize else filesize)

        frame = rawdata[rawdata.rfind(START_BYTES) :]

        # Checking if the image has been fully received
        if not frame.endswith(STOP_BYTES):
            return self.prevFrame

        self.prevFrame = frame
        return frame

    @promptError
    def startPreview(self) -> None:
        """
        startPreview : Starts seperate process for capturing preview,
        releases camera lock to the process.
        """
        self.isPreviewing = True

        self._cleanMovieFile()

        self.frameCount = 0
        self.previewStartTime = time.time_ns()

        self.cam.exit()
        self.previewProcess = subprocess.Popen(
            ["gphoto2", "--capture-movie", "--force-overwrite"],
            stderr=subprocess.STDOUT,
            stdout=self.logfile,
            cwd=os.path.dirname(MOVIE_PATH)
        )
        # , "--stdout", "|",
        # "ffmpeg", "-i", "-", "-f", "mjpeg", "out.avi", "-y"])
        logger.info("POPEN Liveview capture started")

    @promptError
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
        logger.info("Mean FPS since last clip: %s", str(fps))

    def _closeLog(self) -> None:
        self.logfile.close()

    def _cleanUp(self) -> None:
        exitFunctions =  (
            self.cam.exit, 
            self.stopPreview, 
            self._cleanMovieFile,
            self._clearGphoto,
            self._closeLog
        )

        for func in exitFunctions:
            try:
                func()
            finally:
                pass


    @promptError
    def getAbilities(self) -> tuple:
        return tuple(self.cam.get_abilities())

    @promptError
    def getAbout(self):
        return self.cam.get_about()

    @promptError
    def getConfig(self):
        return self.cam.get_config()

    @promptError
    def getManual(self):
        return self.cam.get_manual()

    @promptError
    def getPortInfo(self):
        return self.cam.get_port_info()

    @promptError
    def getSimpleConfig(self):
        return self.cam.get_simple_config()

    @promptError
    def getStorageInfo(self):
        return self.cam.get_storageinfo()

    @promptError
    def getSummary(self):
        return self.cam.get_summary()

    @promptError
    def listConfig(self):
        return self.cam.list_config()


if __name__ == "__main__":
    cam = CameraWrapper()
