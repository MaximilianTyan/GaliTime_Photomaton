#!/bin/env python3
#encoding:utf-8
#coding:utf-8


import gphoto2 as gp
import subprocess
from PyQt5.QtWidgets import QMessageBox

def popError(func):
	def handled(*args):
		try:
			retval = func(*args)
		except Exception as err:
			QMessageBox.critical(None, "Camera error", f"An error occured in function \n{func}:\n {err}")
			return None
		return retval

	return handled

class CameraWrapper():
	def __init__(self):
		self.cam = gp.Camera()
		self.preview_process = None
	
	@popError
	def connect(self):
		self.cam.init()

	@popError
	def list_cams(self):
		return [i for i in gp.Camera.autodetect()]

	@popError
	def takePhoto(self, saveFolder) -> str:
		photoPath = self.cam.capture(gp.GP_CAPTURE_IMAGE)
		photoFile = self.cam.file_get(photoPath.folder, photoPath.name, gp.GP_FILE_TYPE_NORMAL)
		photoFile.save(saveFolder)
		self.cam.file_delete(photoPath.folder, photoPath.name)

	@popError
	def static_preview(self): #return camera file object
		return self.cam.capture_preview()
	
	def start_preview(self):
		self.preview_process = subprocess.Popen(
			["gphoto2", "gphoto2", "--capture-movie", "--force-overwrite"])
			# , "--stdout", "|",
			# "ffmpeg", "-i", "-", "-f", "mjpeg", "out.avi", "-y"])
		print("[POPEN] Liveview capture started")
	
	def stop_preview(self):
		if self.preview_process is not None:
			self.preview_process.terminate()
		print("[POPEN] Liveview capture stopped")
	
	@popError
	def get_abilities(self):
		return self.cam.get_abilities()

	@popError
	def get_about(self):
		return self.cam.get_about()
	
	@popError
	def get_config(self):
		return self.cam.get_config()

	@popError
	def get_manual(self):
		return self.cam.get_manual()

	@popError
	def get_port_info(self):
		return self.cam.get_port_info()

	@popError
	def get_simple_config(self):
		return self.cam.get_simple_config()
	
	@popError
	def get_storageinfo(self):
		return self.cam.get_storageinfo()
	
	@popError
	def get_summary(self):
		return self.cam.get_summary()
	
	@popError
	def list_config(self):
		return self.cam.list_config()


	def __del__(self):
		if self.cam is not None:
			self.cam.exit()

if __name__ == "__main__":
	cam = CameraWrapper()

