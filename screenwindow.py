#!/bin/env python3
#encoding:utf-8
#coding:utf-8

from PyQt5.QtWidgets import QMainWindow, QLabel, QFrame, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtCore import Qt

import vlc

class ScreenWindow(QMainWindow):
	def __init__(self, cam):
		super().__init__()
		self.setWindowTitle("Aperçu")

		self.cam = cam
		self.decorFile = ""
		
		self.screenPage()
		
		self.show()
		
		self.shortcutSetup()
		self.setupMedia()
	
	def setupMedia(self):
		# Setup VLC video manager
		self.VLCinstance = vlc.Instance()
		self.VLCmediaplayer = self.VLCinstance.media_player_new()

		# Link Media player output to a widget
		self.VLCmediaplayer.set_xwindow(int(self.screen.winId()))

		# Return input handling to Qt Widget
		self.VLCmediaplayer.video_set_mouse_input(False)
		self.VLCmediaplayer.video_set_key_input(False)

		self.VLCmediaplayer.event_manager() \
			.event_attach(
				vlc.EventType.MediaPlayerStopped, 
				self.reset)

	def shortcutSetup(self):
		self.FullScreenSC = QShortcut("F11", self)
		self.FullScreenSC.activated.connect(self.toggleFullscreen)

	def toggleFullscreen(self, *args):
		self.close()
		if self.isFullScreen():
			self.showNormal()
		else:
			self.showFullScreen()

	
	def screenPage(self):
		self.label = QLabel()

		self.defaultImage = QPixmap("ressources/default_cam_view.png")
		self.label.setPixmap(self.defaultImage)

		self.label.setAlignment(Qt.AlignCenter)
		self.label.setStyleSheet("font-size: 100px; \
			color:white; \
			background-color: transparent")


		self.screen = QFrame()

		# Layout allowing screen to have the same size as label
		layout = QVBoxLayout()
		layout.setContentsMargins(0, 0, 0, 0)
		layout.setSpacing(0)
		self.label.setLayout(layout)
		layout.addWidget(self.screen)


		self.setCentralWidget(self.label)
		self.reset()

	def showText(self, text):
		self.label.setText(str(text))
	
	def reset(self, *args):
		self.label.setPixmap(self.defaultImage)

	def resetOnMediaEnd(self, Event):
		if self.VLCmedia.get_state() == vlc.State.Ended:
			self.reset()


	def startPreview(self):
		# Launching capture command
		self.cam.start_preview()

		self.VLCmedia = self.VLCinstance.media_new("movie.mjpg")
		self.VLCmedia.parse()
		self.VLCmedia.event_manager() \
			.event_attach(
				vlc.EventType.MediaStateChanged, 
				self.resetOnMediaEnd)

		self.VLCmediaplayer.set_media(self.VLCmedia)
		self.VLCmediaplayer.play()

		self.showText(None)
	
	def stopPreview(self):
		self.VLCmediaplayer.stop()
		self.reset()
	
	
