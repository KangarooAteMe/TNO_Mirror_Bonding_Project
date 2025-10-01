
from detection import Detection
import numpy as np
import cv2 as cv
from math import atan2


class blockDetection(Detection):
    def __init__(self):
        pass

    def nothing(self, x):
        pass

    def findContour(self, im):
        
       
        cv.namedWindow("Edges")
        
        img = cv.imread(im)
        imgres = cv.resize(img, (1000, 1000), interpolation=cv.INTER_CUBIC) #resize the image, interpolation to keep details where possible
        grey = cv.cvtColor(imgres, cv.COLOR_BGR2GRAY) #convert to greyscale

        ########################################################
        # use dilation/erosion to try and remove noise
        ########################################################
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5,5))
        final = cv.morphologyEx(grey, cv.MORPH_OPEN, kernel)
       
        ########################################################
        # Use trackbars to find the ideal lower and upper thresholds
        ########################################################
        
        cv.createTrackbar("Min Threshold", "Edges", 0, 255, self.nothing)
        cv.createTrackbar("Max Threshold", "Edges", 0, 255, self.nothing)
        while True:
            im_copy = imgres.copy()
            thresh1 = int(max(0, 0.66 * cv.getTrackbarPos("Min Threshold", "Edges")))

            thresh2 = int(min(255, 1.33 * cv.getTrackbarPos("Max Threshold", "Edges")))
            
            self.edgesfin = cv.Canny(final, thresh1, thresh2) # Edge detection

            cv.imshow("Original", self.edgesfin)
            cv.waitKey(300)
            self.contours, _ = cv.findContours(self.edgesfin, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE) # find the contours of the edges

            for i, a in (enumerate(self.contours)):
                area = cv.contourArea(a)
                if area < 5: # skip very small contours
                    continue
                
                self.finimg = cv.drawContours(im_copy, [a], -1, (0,255,0), 3)
                self.getCoordinates(a)
                self.getOrientation(a, im_copy)
            cv.imshow("Edges", self.finimg)
            cv.waitKey(300)
            

        return self.contours


    def getCoordinates(self, contours):
        M = cv.moments(contours)
        if M["m00"] == 0:
            return None, None
        cx = int(M["m10"] / M["m00"]) #use Moments to find centerx coordinate of block
        cy = int(M["m01"] / M["m00"]) #use Moments to find centery coordinate of block
        center = (cx, cy)
        cv.putText(self.finimg, "Center", center, cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
        cv.circle(self.finimg, center, 5, (255,0,0), -1)
    


    def framegetter(self, frame):
        if frame is None:
            print("Failed to grab frame")
            return None
        self.frame = frame
        return frame

    def getOrientation(self, fincont, img):


        rotimg = cv.minAreaRect(fincont) #rectangle around the contour
        box = cv.boxPoints(rotimg)
        box = box.astype(int)
        self.rotation = rotimg[-1] #last value of minarearect is angle

        cntr = (int(rotimg[0][0]), int(rotimg[0][1]))

        ############################################
        #Correct the rotations
        ############################################
        if self.rotation < -45:
            self.rotation = (90 + self.rotation)

        else:
            self.rotation = self.rotation

        #######################################################
        # code to find side that deviates, currently not entirely functional,
        # compares all contourpoints' distance to the midpoint of the shape.the code
        # works by quadrant of the contour instead of sides, this means that diagonal blocks arent computed correctly
        # and corners are being seen as the biggest deviating point in the diagonal blocks. fix by assigning points to a specific side
        # also check if comparing only the midpoints of each side would work.
        ########################################################

        center = (cntr[0], cntr[1])
        contourpoints = fincont.reshape(-1, 2)
        distance = np.linalg.norm(contourpoints - center, axis=1)
        sides = contourpoints - center
        angles = np.degrees(np.arctan2(sides[:,1], sides[:,0]))

        left_side = contourpoints[(angles > 135) | (angles < -135)]
        right_side = contourpoints[(angles < 45) & (angles > -45)]
        top_side = contourpoints[(angles >= 45) & (angles <= 135)]
        bottom_side = contourpoints[(angles < -45) & (angles > -135)]
        deviating_side = min((left_side, right_side, top_side, bottom_side), key=lambda side: np.abs(np.mean(np.linalg.norm(side - center, axis=1)) - np.mean(distance)))
        cv.polylines(img, [deviating_side.reshape(-1, 1, 2).astype(np.int32)], False, (0,0,255), 2)

        label = "  Rotation Angle: " + str(self.rotation)
        
        cv.putText(img, label, (cntr[0], cntr[1]), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1, cv.LINE_AA)
        
        print("Rotation: ", int(self.rotation))
        return self.rotation

