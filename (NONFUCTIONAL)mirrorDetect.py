from detection import Detection
import cv2 as cv
import numpy as np

class MirrorDetect(Detection):
	def __init__ (self, im_path):

		self.image = cv.imread(im_path, cv.IMREAD_GRAYSCALE) ## change reference image to grayscale
		self.contour = None # initialise contour as none
		self.coordinates = []
		
		self.sift = cv.SIFT_create(nfeatures=1000) # start sift
		self.kp, self.des = self.sift.detectAndCompute(self.image, None)
		
		FLANN_INDEX_KDTREE = 1
		
		index_parameters = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
		search_parameters = dict(checks=50)
		self.flann = cv.FlannBasedMatcher(index_parameters, search_parameters)
		
		_, thresh = cv.threshold(self.image, 127, 255, cv.THRESH_BINARY)
		
		contours, _ = cv.findContours(thresh, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
		if contours:
			self.ref_contour = max(contours, key=cv.contourArea)
			
		else:
			self.ref_contour = None
	
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
	
	def findContour(self, crd):
		
		if crd is not None:
			cv.polylines(self.frame, [np.int32(crd)], True, (0, 255, 0), 3, cv.LINE_AA)
			if crd:
				self.handler.update_coordinates(crd)


	
	def getCoordinates(self):
		MATCHES_NEEDED = 10
		greyscale_image = cv.cvtColor(self.frame, cv.COLOR_BGR2GRAY)
		self.kp1, self.des1 = self.sift.detectAndCompute(greyscale_image, None)
		if self.des1 is None:
			print("[DEBUG] No descriptors found in current frame.")
			return None, None
		matches = self.flann.knnMatch(self.des, self.des1, k=2)
		print(f"[DEBUG] Total matches found: {len(matches)}")

		best_matches = []
		
		for m, n in matches:
			if m.distance < 0.9 * n.distance:
				best_matches.append(m)
		print(f"[DEBUG] Good matches after ratio test: {len(best_matches)}")
		cv.imshow("test", self.image)
		cv.waitKey(0)
		cv.destroyAllWindows()

		match_vis = cv.drawMatches(self.image, self.kp, greyscale_image, self.kp1, best_matches, None, flags=cv.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
		cv.imshow("Matches", match_vis)
		cv.waitKey(0)
		cv.destroyAllWindows()
				
		if len(best_matches) < MATCHES_NEEDED:
			print(f"[DEBUG] Not enough matches ({len(best_matches)}/{MATCHES_NEEDED})")
			return None, None
		src_points = np.float32([self.kp[m.queryIdx].pt for m in best_matches]).reshape(-1, 1, 2)
		dst_points = np.float32([self.kp1[m.trainIdx].pt for m in best_matches]).reshape(-1, 1, 2)
		
		
					
		M, mask = cv.findHomography(src_points, dst_points, cv.RANSAC, 5.0)
		
		if M is None:
			print("[DEBUG] Homography could not be computed.")
			return None, None
		print (self.ref_contour.shape)
		print("[DEBUG] Homography matrix computed.")
		epsilon = 0.01 * cv.arcLength(self.ref_contour, True)
		approx_contour = cv.approxPolyDP(self.ref_contour, epsilon, True)
		contour = approx_contour.astype(np.float32)
		if contour.ndim == 2:
			contour = contour.reshape(-1, 1, 2)
		contour_pts = cv.perspectiveTransform(contour, M)
		contour_coords = [(int(x), int(y)) for [[x, y]] in contour_pts]
		frame_with_contour = self.frame.copy()
		cv.polylines(frame_with_contour, [np.int32(contour_pts)], True, (0, 255, 0), 3, cv.LINE_AA)
		cv.imshow("Transformed Contour", frame_with_contour)
		cv.waitKey(0)
		cv.destroyAllWindows()
		
		M_moments = cv.moments(contour_pts)
		if M_moments['m00'] != 0:
			centerx = int(M_moments['m10'] / M_moments['m00'])
			centery = int(M_moments['m01'] / M_moments['m00'])
			center_coord = (centerx, centery)
			print(f"[DEBUG] Center found at: {center_coord}")
		else:
			center_coord = None
			print("[DEBUG] Center could not be computed (zero moments).")
		return contour_coords, center_coord
		

	
