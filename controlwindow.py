#!/bin/env python3
#encoding:utf-8
#coding:utf-8

from PyQt5.QtWidgets import QMainWindow, QWidget, QFileDialog
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit, QDateEdit, QAbstractSpinBox
from PyQt5.QtWidgets import QShortcut

from PyQt5.QtCore import Qt, QTimer, QDate

import os, json

import stylesheet

class ControlWindow(QMainWindow):
	def __init__(self, screen, cam):
		super().__init__()
		self.setWindowTitle("GaliTime")

		self.screen = screen
		self.cam = cam
		
		self.eventName = ""
		self.eventDate = QDate.currentDate()
		self.saveFolder = ""

		self.photoNumber = 0
		self.emailNumber = 0
		
		self.timer = QTimer()
		self.timer.timeout.connect(self.tickTimer)

		self.optionsPage()
		#self.camOptionsPage()

		self.show()
		self.shortcutSetup()

	def shortcutSetup(self):
		self.FullScreenSC = QShortcut("F11", self)
		self.FullScreenSC.activated.connect(self.toggleFullscreen)

	def toggleFullscreen(self, Event):
		self.close()
		if self.isFullScreen():
			self.showNormal()
		else:
			self.showFullScreen()

	def closeEvent(self, event) -> None:
		self.screen.close()
		event.accept()
	

	def optionsPage(self):
		# Main layout, vertical, contains Title, Button Layout
		MainContainer = QWidget(self)
		MainVLayout= QVBoxLayout()
		MainContainer.setLayout(MainVLayout)

		# 1. Label "GaliTime Options"
		TitleLabel = QLabel("GaliTime - Options")
		TitleLabel.setStyleSheet("font-size: 50px")
		TitleLabel.setAlignment(Qt.AlignCenter)
		MainVLayout.addWidget(TitleLabel)

		# 2 Layout EventName
		NameHLayout = QHBoxLayout()
		MainVLayout.addLayout(NameHLayout)

		# 2.1 Line Edit
		self.EventInput = QLineEdit(self.eventName)
		self.EventInput.setPlaceholderText("Nom de l'événement")
		self.EventInput.setAlignment(Qt.AlignCenter)
		NameHLayout.addWidget(self.EventInput)

		# 2.2 Validate Button
		ValidateNameButton = QPushButton("Valider")
		ValidateNameButton.setMaximumSize(100, 30)
		ValidateNameButton.setMinimumSize(100, 30)
		ValidateNameButton.clicked.connect(self.changeEventName)
		NameHLayout.addWidget(ValidateNameButton)

		# 3. Layout EventDate
		DateHLayout = QHBoxLayout()
		MainVLayout.addLayout(DateHLayout)

		# 3.1 Date
		self.EventDateInput = QDateEdit(self.eventDate)
		self.EventDateInput.setDisplayFormat("dd/MM/yyyy")
		self.EventDateInput.setAlignment(Qt.AlignCenter)
		self.EventDateInput.setButtonSymbols(QAbstractSpinBox.NoButtons)
		DateHLayout.addWidget(self.EventDateInput)

		# 3.2 Date
		ValidateDateButton = QPushButton("Valider")
		ValidateDateButton.clicked.connect(self.changeEventDate)
		DateHLayout.addWidget(ValidateDateButton)

		# 4 Secondary layout SaveFolder
		SaveHLayout = QHBoxLayout()
		MainVLayout.addLayout(SaveHLayout)
		
		# 4.1 SaveFolder label
		self.SaveFolderLabel = QLabel("Dossier d'enregistrement:\n" + self.saveFolder)
		self.SaveFolderLabel.setAlignment(Qt.AlignCenter)
		SaveHLayout.addWidget(self.SaveFolderLabel)

		# 4.2 Browe button
		BrowseButton = QPushButton("Parcourir")
		BrowseButton.clicked.connect(self.chooseSaveFolder)
		# BrowseButton.setMaximumSize(100, 30)
		# BrowseButton.setMinimumSize(100, 30)
		SaveHLayout.addWidget(BrowseButton)
		
		# 5 Secondary layout DecorFile
		DecorHLayout = QHBoxLayout()
		MainVLayout.addLayout(DecorHLayout)
		
		# 5.1 Decorfile label
		self.DecorFileLabel = QLabel("Image de Décoration:\n" + self.screen.decorFile)
		self.DecorFileLabel.setAlignment(Qt.AlignCenter)
		DecorHLayout.addWidget(self.DecorFileLabel)

		# 5.2 Browe button
		BrowseButton2 = QPushButton("Choisir")
		BrowseButton2.clicked.connect(self.chooseDecorFile)
		# BrowseButton2.setMaximumSize(100, 30)
		# BrowseButton2.setMinimumSize(100, 30)
		DecorHLayout.addWidget(BrowseButton2)

		# 6 Error Label
		self.errorLabel = QLabel()
		self.errorLabel.setAlignment(Qt.AlignCenter)
		self.errorLabel.setStyleSheet("color: rgb(200,50,50)")
		MainVLayout.addWidget(self.errorLabel)
		
		# 7 Save & return button 
		ReturnButton = QPushButton("Enregistrer")
		ReturnButton.setStyleSheet(stylesheet.BigRedButton)
		ReturnButton.clicked.connect(self.controlPageCheck)
		MainVLayout.addWidget(ReturnButton)

		TitleLabel.setFocus()
		self.setCentralWidget(MainContainer)

	def chooseSaveFolder(self):
		self.saveFolder = QFileDialog.getExistingDirectory(self,
			caption="Dossier d'enregistrement",
			directory=os.path.abspath("~"))
		self.SaveFolderLabel.setText("Dossier d'enregistrement:\n" + self.saveFolder)
		
	def chooseDecorFile(self):
		output = QFileDialog.getOpenFileName(self,
			caption="Image de décor",
			directory= os.path.abspath("~"))
		self.screen.decorFile = output[0]
		self.DecorFileLabel.setText("Image de décor:\n" + self.screen.decorFile)
	
	def changeEventName(self):
		if self.EventInput.text().strip() != "":
			self.eventName = self.EventInput.text()
			self.EventInput.setStyleSheet("background-color: rgb(100, 200, 100)")
		else:
			self.EventInput.setStyleSheet("background-color: rgb(200, 100, 100)")
	
	def changeEventDate(self):
		date = self.EventDateInput.date()
		if date.isValid():
			self.eventDate = self.EventDateInput.date()
			self.EventDateInput.setStyleSheet("background-color: rgb(100, 200, 100)")
		else:
			self.EventDateInput.setStyleSheet("background-color: rgb(200, 100, 100)")
	
	def writeInfoFile(self):
		infodict = {
			"eventname" : self.eventName,
			"date" : self.eventDate,
			"photo_number" : self.photoNumber,
			"email_number" : self.emailNumber
			}
		with open(self.saveFolder + "/info.json", "xt") as file:
			file.write(json.dump(infodict))

	def initSaveFolder(self):
		os.mkdir(self.saveFolder + "/raw_photos")
		os.mkdir(self.saveFolder + "/emails_folder")

		self.writeInfoFile()
	
	def controlPageCheck(self):
		if self.eventName.strip() == "":
			self.errorLabel.setText("Le nom de l'événement ne doit pas être vide")
			return
		if self.saveFolder.strip() == "":
			self.errorLabel.setText("Le dossier d'enregistrement doit être valide")
			return
		if self.screen.decorFile.strip() == "":
			self.errorLabel.setText("Le fichier de décoration doit être valide")
			return
		
		self.initSaveFolder()

		self.controlPage()



	def controlPage(self):
		# Main layout, vertical, contains Everything
		MainContainer = QWidget(self)
		MainVLayout= QVBoxLayout()
		MainContainer.setLayout(MainVLayout)

		# 1 Label "GaliTime"
		TitleLabel = QLabel("GaliTime")
		TitleLabel.setAlignment(Qt.AlignCenter)
		TitleLabel.setStyleSheet("font-size: 50px")
		MainVLayout.addWidget(TitleLabel)

		# 2 Label Event
		EventLabel = QLabel(self.eventName)
		EventLabel.setAlignment(Qt.AlignCenter)
		EventLabel.setStyleSheet("font-size: 30px")
		MainVLayout.addWidget(EventLabel)
		
		# 3 Take Photo
		PhotoButton = QPushButton("Prendre la photo")
		PhotoButton.setStyleSheet(stylesheet.BigBlueButton)
		PhotoButton.clicked.connect(self.startCountdown)
		MainVLayout.addWidget(PhotoButton)
		
		# 4 Email button
		EmailButton = QPushButton("Envoyer par mail")
		EmailButton.setStyleSheet(stylesheet.BigBlueButton)
		MainVLayout.addWidget(EmailButton)
		
		# 5 Print button
		PrintButton = QPushButton("Imprimer la photo")
		PrintButton.setStyleSheet(stylesheet.BigBlueButton)
		MainVLayout.addWidget(PrintButton)
		
		# 6 Option Layout
		OptionHLayout = QHBoxLayout()
		MainVLayout.addLayout(OptionHLayout)

		# 6.1 Options button
		OptionButton = QPushButton("Options")
		OptionButton.clicked.connect(self.optionsPage)
		OptionHLayout.addWidget(OptionButton)

		# 6.2 Camera options button
		CamOptionButton = QPushButton("Camera")
		CamOptionButton.clicked.connect(self.camOptionsPage)
		OptionHLayout.addWidget(CamOptionButton)

		self.setCentralWidget(MainContainer)

	def startCountdown(self):
		self.timer.countdown = 3
		self.timer.start(1000)
	
	def tickTimer(self):
		if self.timer.countdown <= -1:
			self.screen.reset()
			self.timer.stop()
		elif self.timer.countdown == 0:
			self.screen.showText("SOURIEZ")
			self.cam.takePhoto(self.saveFolder)
		else:
			self.screen.showText(self.timer.countdown)
		self.timer.countdown -= 1



	def camOptionsPage(self):
		MainContainer = QWidget()
		MainVLayout = QVBoxLayout()
		MainContainer.setLayout(MainVLayout)

		# 2 Available cameras Layout
		CamsHLayout = QHBoxLayout()
		MainVLayout.addLayout(CamsHLayout)

		# 2.1 Choice box listing items
		self.CamsChoiceBox = QComboBox()
		self.updateCamList()
		CamsHLayout.addWidget(self.CamsChoiceBox)

		# 2.2 Update button
		CamsUpdateButton = QPushButton("MAJ Liste caméra")
		CamsUpdateButton.clicked.connect(self.updateCamList)
		CamsHLayout.addWidget(CamsUpdateButton)

		# 3 Info Grid Layout
		InfoGridLayout = QGridLayout()
		MainVLayout.addLayout(QGridLayout)

		# 3.1 Abilities Layout
		AbilitiesVLayout = QVBoxLayout()
		InfoGridLayout.addLayout(AbilitiesVLayout, 0, 0)

		# 3.1.1 Abilities list button
		AbilitiesUpdateButton = QPushButton("MAJ Abilities")
		AbilitiesUpdateButton.clicked.connect(self.updateAbilities)
		AbilitiesVLayout.addWidget(AbilitiesUpdateButton)

		# 3.1.2 Abilities list button
		self.AbilitiesText = QTextEdit()
		AbilitiesVLayout.addWidget(self.AbilitiesText)

		# 3.2 Config Layout
		ConfigVLayout = QVBoxLayout()
		InfoGridLayout.addLayout(ConfigVLayout, 0, 1)

		# 3.2.1 Config list button
		ConfigUpdateButton = QPushButton("MAJ Config")
		ConfigUpdateButton.clicked.connect(self.updateConfig)
		ConfigVLayout.addWidget(ConfigUpdateButton)

		# 3.2.2 Config list button
		self.ConfigText = QTextEdit()
		ConfigVLayout.addWidget(self.ConfigText)

		# 3.3 About Layout
		AboutVLayout = QVBoxLayout()
		InfoGridLayout.addLayout(AboutVLayout, 1, 0)

		# 3.3.1 About list button
		AboutUpdateButton = QPushButton("MAJ About")
		AboutUpdateButton.clicked.connect(self.updateAbout)
		AboutVLayout.addWidget(AboutUpdateButton)

		# 3.3.2 About list button
		self.AboutText = QTextEdit()
		AboutVLayout.addWidget(self.AboutText)

		# 3.4 Summary Layout
		SummaryVLayout = QVBoxLayout()
		InfoGridLayout.addLayout(SummaryVLayout, 1, 1)

		# 3.4.1 Summary list button
		SummaryUpdateButton = QPushButton("MAJ Summary")
		SummaryUpdateButton.clicked.connect(self.updateSummary)
		SummaryVLayout.addWidget(SummaryUpdateButton)

		# 3.4.2 Summary list button
		self.SummaryText = QTextEdit()
		SummaryVLayout.addWidget(self.SummaryText)


		# 4 Save & return button 
		ReturnButton = QPushButton("Enregistrer")
		ReturnButton.setStyleSheet(stylesheet.BigRedButton)
		ReturnButton.clicked.connect(self.controlPage)
		MainVLayout.addWidget(ReturnButton)

		self.setCentralWidget(MainContainer)

	def updateCamList(self):
		self.CamsChoiceBox.clear()
		cam_list = self.cam.list_cams()

		if len(cam_list) == 0 or cam_list is None:
			self.CamsChoiceBox.addItem("None")

		for cam in cam_list:
			self.CamsChoiceBox.addItem(cam)
	
	@staticmethod
	def filteredDir(obj):
		outdict = {}

		for attr in dir(obj):
			if attr.startswith('_'):
				continue

			if attr in ("acquire","append","disown","next","own", "this", "thisown"):
				continue

			if attr.startswith("reserved"):
				continue

			attr_value = obj.__getattribute__(attr)
			try:
				text_value = attr_value()
			except TypeError:
				text_value = attr_value
			
			if isinstance(text_value, str):
				text_value = '"' + text_value + '"'
			
			outdict[attr] = text_value
		
		return outdict

	@staticmethod
	def HTMLTablize(datadict):
		text = "<table>\n \
					<tr> \n \
						<td> Attribute </td>\n \
						<td> Value </td>\n \
					</tr>\n"

		for key, value in datadict.items():
			text += f"<tr> \n \
						<td> {key} </td>\n \
						<td> {value} </td>\n \
					</tr>\n"
		
		text+= "<table>"
		return text

	
	def updateAbilities(self):
		cam_abilities = self.filteredDir( self.cam.get_abilities() )
		self.AbilitiesText.setText( self.HTMLTablize(cam_abilities) )
		
	def updateConfig(self):
		cam_config = self.filteredDir( self.cam.get_config() )
		self.ConfigText.setText( self.HTMLTablize(cam_config) )
	
	def updateAbout(self):
		cam_about = self.filteredDir( self.cam.get_about() )
		self.AboutText.setText( self.HTMLTablize(cam_about) )

	def updateSummary(self):
		cam_summary = self.filteredDir( self.cam.get_summary() )
		self.SummaryText.setText( self.HTMLTablize(cam_summary) )