import cv2 as cv
import numpy as np

class Camera:
	def __init__(self):
		self.vc = cv.VideoCapture(0)
		if not self.vc.isOpened(): 
			raise Exception("Could not open video device")
	
	def __del__(self):
		cv.destroyAllWindows()
		if self.vc.isOpened():
			self.vc.release()
	def get_frame(self):
		ret, frame = self.vc.read()
		if not ret:
			return None
		return frame
	
	def record(self):
		while True:
			ret, frame = self.vc.read()
			
			if not ret:
				print("Failed to grab frame")
				break
			cv.imshow("Camera", frame)
			if cv.waitKey(1) & 0xFF == ord('q'):
				break
	
