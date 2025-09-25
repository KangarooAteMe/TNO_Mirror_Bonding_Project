

from detection import Detection
import cv2 as cv
import numpy as np

class MirrorDetect(Detection):
	def __init__ (self):

		############
		#HSV_values (subject to change)
		###########
		self.lr = np.array([144, 113, 0]) 
		self.ur = np.array([180, 255, 255])
		self.lr2 = np.array([170, 113, 0])
		self.ur2 = np.array([180, 255, 255])

		self.kernel = np.ones((5,5), np.uint8)
		self.last_contours = []
		self.frame = None
	def __del__ (self):
		pass
	
	def update_coordinates(self, coords):
		self.coordinates = coords
		coords.get_coordinates(coords)
		return coords

	def framegetter(self, frame):
		if frame is None:
			print("Failed to grab frame")
			return None
		self.frame = frame
		return frame
	
	def findContour(self):
		hsv = cv.cvtColor(self.frame, cv.COLOR_BGR2HSV)
		mask = cv.inRange(hsv, self.lr, self.ur)
		mask2 = cv.inRange(hsv, self.lr2, self.ur2)
		mask = cv.bitwise_or(mask, mask2)
    
		mask = cv.morphologyEx(mask, cv.MORPH_OPEN, self.kernel)
		mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, self.kernel)
    
		contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
     
		output = self.frame.copy()
		smooth_cnt = []
		if contours:
			mirror_cnts = sorted(contours, key=cv.contourArea, reverse=True)[:5]
			for i, cnt in enumerate(mirror_cnts):
				epsilon = 0.02 * cv.arcLength(cnt, True)
				aprox = cv.approxPolyDP(cnt, epsilon, True)
				prev = self.last_contours[i] if i < len(self.last_contours) else None
				smooth = self.wrap_contour(prev, aprox, 0.5)
				smooth_cnt.append(smooth)

		
		
		self.last_contours = smooth_cnt
		cv.drawContours(output, smooth_cnt, -1, (0, 255, 0), 2)
		self.output_frame = output
		self.mask_frame = mask
		return output, mask
	
	def getCoordinates(self):
		mid= []
		for cnt in self.last_contours:
			M_moments = cv.moments(cnt)
			if M_moments['m00'] != 0:
				centerx = int(M_moments['m10'] / M_moments['m00'])
				centery = int(M_moments['m01'] / M_moments['m00'])
				mid.append((centerx, centery))
		
		else:
			mid.append(None)

		print(mid)
		self.flatlist = [x for mini in mid if mini is not None for x in mini]
		print(self.flatlist)
		return self.flatlist
	
	def findOrientation(flatlist, abs1, abs2, abs3):
		Manhatten1 = sum(abs(flatlist - abs1) for flatlist, abs1 in zip(flatlist, abs1))
		Manhatten2 = sum(abs(flatlist- abs2) for flatlist, abs2 in zip(flatlist, abs2))
		Manhatten3 = sum(abs(flatlist - abs3) for flatlist, abs3 in zip(flatlist, abs3))
		Manhattenmatch = min(Manhatten1, Manhatten2, Manhatten3)

		return Manhattenmatch



	def wrap_contour(self, prev, current, alpha=0.5):
		if prev is None or len(prev) != len(current):
			return current
		return np.int32(prev * (1 - alpha) + current * alpha)

	
