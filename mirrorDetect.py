

from detection import detection
import cv2 as cv
import numpy as np

class mirrordetect(Detection):
	def __init__ (self):

		############
		#HSV_values (subject to change, currently on red)
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

		mask = cv.bitwise_or(mask, mask2) #combine the masks to smoothen the contour
    
		mask = cv.morphologyEx(mask, cv.MORPH_OPEN, self.kernel) # dilate, erode mask
		mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, self.kernel) #erode, dilate mask
    
		contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
     
		output = self.frame.copy()
		smooth_cnt = []
		if contours:
			mirror_cnts = sorted(contours, key=cv.contourArea, reverse=True)[:5] # take 5 biggest contours
			for i, cnt in enumerate(mirror_cnts):
				epsilon = 0.02 * cv.arcLength(cnt, True)
				aprox = cv.approxPolyDP(cnt, epsilon, True) # approximate contours
				prev = self.last_contours[i] if i < len(self.last_contours) else None # store contour
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
				centerx = int(M_moments['m10'] / M_moments['m00']) # find centerx of each contour
				centery = int(M_moments['m01'] / M_moments['m00'])# find centery of each contour
				mid.append((centerx, centery))
		
		else:
			mid.append(None)

		print(mid)
		self.flatlist = [x for mini in mid if mini is not None for x in mini] # make a 1Dlist of each point
		print(self.flatlist)
		return self.flatlist
	
	def findOrientation(flatlist, abs1, abs2, abs3):
		keyvaluepair = {
			'Manhatten1' : [abs1, 0],
			'Manhatten2' : [abs2, 0],
			'Manhatten3' : [abs3, 0]
			}

		Manhatten1 = sum(abs(flatlist - abs1) for flatlist, abs1 in zip(flatlist, abs1)) # abs difference of found coordinates and first set of static coordinates
		keyvaluepair['Manhatten1'][1] = Manhatten1 # difference is put in the dict
		Manhatten2 = sum(abs(flatlist- abs2) for flatlist, abs2 in zip(flatlist, abs2))
		keyvaluepair['Manhatten2'][1] = Manhatten2
		Manhatten3 = sum(abs(flatlist - abs3) for flatlist, abs3 in zip(flatlist, abs3))
		keyvaluepair['Manhatten3'][1] = Manhatten3
		return min(keyvaluepair.values(), key=lambda x: x[1])[0]

	def wrap_contour(self, prev, current, alpha=0.5):
		if prev is None or len(prev) != len(current):
			return current
		return np.int32(prev * (1 - alpha) + current * alpha) #blend last and current contour to make it smoother. 0.5 means half/half

	
