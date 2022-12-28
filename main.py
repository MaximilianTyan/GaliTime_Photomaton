#!/bin/env python3
#encoding:utf-8
#coding:utf-8

import sys
from PyQt5.QtWidgets import QApplication

from controlwindow import ControlWindow
from screenwindow import ScreenWindow
from camera import CameraWrapper

app = QApplication(sys.argv)

cam = CameraWrapper()
screen = ScreenWindow(cam)
main = ControlWindow(screen, cam)

main.show()
screen.show()

cam.connect()
screen.startPreview()

sys.exit(app.exec())
