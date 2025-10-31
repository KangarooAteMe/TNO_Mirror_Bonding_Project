
from detection import detection
import numpy as np
import cv2 as cv
from math import atan2


class blockDetection(detection):
    def __init__(self):
        self.binary = None
        self.contours = None
        self.finimg = None
        self.Pta = None
        self.Ptb = None
        self.middles = None
        self.deviatingside = None
        self.deviatingangle = None
        self.refangle = None
        self.rotation = None
        self.frame = None
        self.centre = None
        self.rotarray = []
        self.centarray = []
        


    def nothing(self, x):
        pass

    def midpointtake(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    def findContour(self, im):
        
       
        cv.namedWindow("Edges")
        
        img = cv.imread(im)
        imgres = cv.resize(img, (2200, 1000), interpolation=cv.INTER_CUBIC) #resize the image, interpolation to keep details where possible
        grey = cv.cvtColor(imgres, cv.COLOR_BGR2GRAY) #convert to greyscale
        grey = cv.medianBlur(grey, 1)

        ########################################################
        # use dilation/erosion to try and remove noise
        ########################################################
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        final = cv.morphologyEx(grey, cv.MORPH_OPEN, kernel)
        final2 = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)

       
        ########################################################
        # Use trackbars to find the ideal lower and upper thresholds
        ########################################################
        
        
        im_copy = imgres.copy()
            
        _, self.binary = cv.threshold(final2, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        self.binary = cv.bitwise_not(self.binary)
            
            
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
            

        self.binary = cv.erode(self.binary, kernel, iterations=7)
            

            
            


        cv.imshow("Original", self.binary)
        cv.waitKey(300)
        self.contours, _ = cv.findContours(self.binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE) 

        for i, a in (enumerate(self.contours)):
            area = cv.contourArea(a)
            if area < 2: 
                continue
                
            self.finimg = cv.drawContours(im_copy, [a], -1, (0,255,0), 3)
            self.getOrientation(a, im_copy)
            cv.imshow("Edges", self.finimg)
            cv.waitKey(300)
            

        return self.contours


    def getcenterCoordinates(self, contours):
        M = cv.moments(contours)
        if M["m00"] == 0:
            return None, None
        cx = int(M["m10"] / M["m00"]) #use Moments to find centerx coordinate of block
        cy = int(M["m01"] / M["m00"]) #use Moments to find centery coordinate of block
        self.center = (cx, cy)
        cv.putText(self.finimg, "Center", self.center, cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
        cv.circle(self.finimg, self.center, 5, (255,0,0), -1)
        return self.center
    
    def getCoordinates(self):
        pass


    def framegetter(self, frame):
        if frame is None:
            print("Failed to grab frame")
            return None
        self.frame = frame
        return frame

    def straightline_true(self, coords, tol=25):
         coords = np.array(coords)
         x = coords[:,0]
         y = coords[:,1]
         m, b = np.polyfit(x, y, 1)  
         res = np.abs(y - (m*x + b))
         return np.mean(res)  

    def getangle(self, p1, p2):
        delta_y = p2[1] - p1[1]
        delta_x = p2[0] - p1[0]
        angle = atan2(delta_y, delta_x) * 180.0 / np.pi
        return angle

    def point_to_line_distance(self, pt, line_start, line_end):
        pt = np.array(pt)
        line_start = np.array(line_start)
        line_end = np.array(line_end)
        line_vec = line_end - line_start
        pt_vec = pt - line_start
        line_len = np.dot(line_vec, line_vec)
        if line_len == 0:
            return np.linalg.norm(pt - line_start)

        t = np.dot(pt_vec, line_vec) / line_len
        if 0 <= t <= 1:
            projection = line_start + t * line_vec
            return np.linalg.norm(pt - projection)
    
    def getOrientation(self, fincont, img):

        currbestdev = -1
        cornerapprox = cv.approxPolyDP(fincont, 0.02 * cv.arcLength(fincont, True), True) 
        
        cornercoords = [tuple(cpt[0]) for cpt in cornerapprox]
        midpointcoords = []
        for corner in range(len(cornerapprox)):
            self.Pta = np.array(cornerapprox[corner][0])
            self.Ptb = np.array(cornerapprox[(corner + 1) % len(cornerapprox)][0])
            self.middles = self.midpointtake(self.Pta, self.Ptb)

            cv.circle(img, (int(self.middles[0]), int(self.middles[1])), 5, (0,255,0), -1)
            cv.circle(img, tuple(cornerapprox[corner][0]), 5, (0,0,255), -1)
            
            #print("Corners: ", tuple(self.Pta), tuple(self.Ptb))
            #print("Midpoint: ", (int(self.middles[0]), int(self.middles[1])))

            

        pts = fincont[:,0,:] 

        side_pts = {i: [] for i in range(len(cornercoords))}
        for pt in pts:
            min_dif = float('inf')
            realside = -1
            for i in range(len(cornercoords)):
                dists = self.point_to_line_distance(pt, cornercoords[i], cornercoords[(i + 1) % len(cornercoords)]) 

                if dists is None:
                    continue
                if dists < min_dif:
                    min_dif = dists
                    realside = i

            if realside != -1:
                side_pts[realside].append(tuple(pt))

        for i, pts in side_pts.items():
            if len(pts) < 2:
                continue
            self.deviation = self.straightline_true(pts)
            if self.deviation > currbestdev:
                currbestdev = self.deviation
                self.deviatingside = (cornercoords[i], cornercoords[(i + 1) % len(cornercoords)])
            
            
        if self.deviatingside:
            self.Pta = np.array(self.deviatingside[0])
            self.Ptb = np.array(self.deviatingside[1])
            self.deviatingangle = self.getangle(self.Pta, self.Ptb)
            self.refangle = self.deviatingangle
            cv.line(img, tuple(self.Pta.astype(int)), tuple(self.Ptb.astype(int)), (0,255,255), 2)


        
        self.rotation = self.refangle
        self.rotation = round(self.rotation, 2)

        

        ############################################
        #Correct the rotations
        ############################################
        if self.rotation < -45:
            self.rotation = (90 + self.rotation)

        else:
            self.rotation = self.rotation

        self.rotarray.append(self.rotation)

        self.centre = np.array(self.getcenterCoordinates(fincont))
        self.centarray.append(self.centre)

     

      
        
        


        label = "  Rotation Angle: " + str(self.rotation)
        textbox = (self.centre[0] - 100, self.centre[1] - 25)
        cv.putText(img, label, textbox, cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 2)


        
        
        return self.rotation, self.centre
        #print("Rotation: ", int(self.rotation))
       

    def getVals(self):
        testrot = self.rotarray
        testcent = self.centarray
        blocks =  dict(zip(testcent, testrot))
        return blocks
