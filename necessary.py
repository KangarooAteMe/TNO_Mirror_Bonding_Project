

import time
import cv2 as cv
import numpy as np
from camera import Camera
from detection import Detection
from blockDetect import blockDetection
from state_enum import program_State
from databuffer import Databuffer
from coordinateconversion import CoordinateConversion
import os 
from Network_client import Network_client
from math import atan2
import sys
from harvesters.core import Harvester
from PyQt6.QtWidgets import QApplication
from window import MainWindow
from pathlib import Path



def main(): 
    IP = "192.168.0.4"
    PORT = 65432

    
    direc = r"C:\Users\basti\Pictures\ims\protoimages"
    findpicture = os.listdir(direc)
    picture = findpicture[0]
    Dir_pic = str(direc + "\\" + picture)

    

  
    block= blockDetection()
    state = program_State.IDLE
    app = QApplication(sys.argv)
    window = MainWindow()
   
    #converter = CoordinateConversion()
    buffer = Databuffer(window, block)
   

   
    netwcl = Network_client(IP, PORT)
    cam = Camera()
    
    
    
    #app.setStyleSheet(Path("Style.qss").read_text())
    
    
    
    netwcl.strt_socket()
    netwcl.connect_client()

    while True:
        state = netwcl.receive_client()
        camera_state = cam.run(state)
        
    
        if camera_state == program_State.GET_BLOCK_COORDS:
            harvest()

            block.findContour(Dir_pic)
            test = buffer.collectVisData()
            netwcl.send_client(test)

        elif camera_state == program_State.PREP_GLUE_1:
            netwcl.send_client("prep_glue_1_start")

        elif camera_state == program_State.PREP_GLUE_2:
            netwcl.send_client("prep_glue_2_start")

        elif camera_state == program_State.GET_MIRROR_COORDS:
            data = window.on_button_click_import()
            coords = buffer.collectfinalPos()
            netwcl.send_client(coords)
           
        elif camera_state == program_State.IDLE:
            print("System is IDLE, waiting for next command...")

        time.sleep(3)

        


    netwcl.disconnect_client()
    netwcl.clse_socket()
    



def networktest():
    ipaddr = "127.0.0.1"
    PORT_num = 65432

  



def pic():
   direc = r"C:\Users\basti\Pictures\ims\protoimages"
   findpicture = os.listdir(direc)
   picture = findpicture[0]
   Dir_pic = str(direc + "\\" + picture)
  
def camtest():
  """Main application function"""
  print("=== Daheng Camera Application ===\n")

  camera = DahengCamera()

  if not camera.initialize():
        sys.exit(1)

    # Discover cameras
  devices = camera.discover_cameras()
  if not devices:
        sys.exit(1)

    # Connect to first camera
  if not camera.connect_camera(1):
      sys.exit(1)

    # Configure camera
  if not camera.configure_camera(exposure_us=20000, gain_db=5.0):
      camera.cleanup()
      sys.exit(1)

    # Start acquisition
  if not camera.start_acquisition():
      camera.cleanup()
      sys.exit(1)

  try:
        # Capture some individual images
        print("\nCapturing 5 individual images...")
        for i in range(5):
            image_data = camera.capture_image()
            if image_data:
                print(f"Captured image {i+1}: {image_data['image'].shape}")
  except KeyboardInterrupt:
        print("\nInterrupted by user")
        
  finally:
        # Always cleanup
        camera.cleanup()
        print("Application finished")

def harvest():
    CTI_FILE_PATH = "C:/Program Files/Daheng Imaging/GalaxySDK/GenTL/Win64/GxGVTL.cti"  # The filepath to the CTI file
   # Create a Harvester instance
    h = Harvester()
    direc = r"C:\Users\basti\Pictures\ims\protoimages"
    h.add_file(CTI_FILE_PATH)
    h.update()
    with h.create() as ia:
        ia.start()
        with ia.fetch() as buffer:
            component = buffer.payload.components[0]
            width = component.width
            height = component.height
            bayer = component.data.reshape((height, width))
            img = cv.cvtColor(bayer, cv.COLOR_BayerRG2BGR)
            img = img[..., ::-1]
            cv.imwrite(os.path.join(direc, "CamCap.bmp"), img)
           # flush the image buffer to prepare for the next image
        ia.stop()
            
    h.reset()



    


class Databuffer:
    def __init__(self, mirror, block):
        self.mir = mirror
        self.blk = block
        self.arrayify = []
        self.i = 0


    def collectVisData(self):    

        datablk = self.blk.getVals(self.i)
        
        if self.i < len(datablk):
            
            self.i = self.i + 1
            return datablk
        else:
            return None

    def collectfinalPos(self):    

        pos = self.mir.getVals(self.i)
        
        if self.i < len(pos):
            
            self.i = self.i + 1
            return pos
        else:
            return None


    def sendoneblock(self):
        pass
       
      



class blockDetection(Detection):
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
        self.combined_list = []
        convert = CoordinateConversion()
        


    def nothing(self, x):
        pass

    def midpointtake(self, ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

    def findContour(self, im):
        
       
        cv.namedWindow("Edges")
        
        img = cv.imread(im)
        grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY) #convert to greyscale
        grey = cv.medianBlur(grey, 1)

        ########################################################
        # use dilation/erosion to try and remove noise
        ########################################################
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (5,5))
        final2 = cv.morphologyEx(grey, cv.MORPH_OPEN, kernel)
        #final2 = cv.morphologyEx(final, cv.MORPH_CLOSE, kernel)

       
        ########################################################
        # Use trackbars to find the ideal lower and upper thresholds
        ########################################################

     
        im_copy = img.copy()
            
        _, self.binary = cv.threshold(final2, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
        self.binary = cv.bitwise_not(self.binary)

        self.bin_copy = self.binary.copy()
        cv.resize(self.bin_copy, (1500,1200))
            
            
        kernel = cv.getStructuringElement(cv.MORPH_RECT, (3,3))
            

        self.binary = cv.erode(self.bin_copy, kernel, iterations=8)
        self.binary = cv.dilate(self.bin_copy, kernel, iterations=0)
            

            
            


        cv.imshow("Original", self.binary)
        cv.waitKey(300)
        self.contours, _ = cv.findContours(self.binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE) 
            #self.contours2, _ = cv.findContours(self.bin_copy, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

        for i, a in (enumerate(self.contours)):
            area = cv.contourArea(a)
            if area < 40: 
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

    def straightline_true(self, coords):
         coords = np.array(coords)
         mean = np.mean(coords, axis=0)
         center = coords - mean
        
    
         _, _, vh = np.linalg.svd(center)
           
         norm = vh[1]   
         
         res = center @ norm
         return np.mean(np.abs(res))

    def calculateRotation(self, p1, p2): 
        delta_y = p2[1] - p1[1]
        delta_x = p2[0] - p1[0]

        angle_rad = atan2(delta_y, delta_x)

        if angle_rad < 0:
            angle_rad += 2 * np.pi

        angle_rad = angle_rad * -1  
        

        return angle_rad
        

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
            cv.putText(self.finimg, "PtA", self.Pta, cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
            cv.circle(self.finimg, self.Pta, 5, (255,0,0), -1)
            self.Ptb = np.array(self.deviatingside[1])
            cv.putText(self.finimg, "PtB", self.Ptb, cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2)
            cv.circle(self.finimg, self.Ptb, 5, (255,0,0), -1)
            self.deviatingangle = self.calculateRotation(self.Pta, self.Ptb)
            self.refangle = self.deviatingangle
            cv.line(img, tuple(self.Pta.astype(int)), tuple(self.Ptb.astype(int)), (0,255,255), 2)


        
        self.rotation = self.refangle
        self.rotation = round(self.rotation, 2)

        

        ############################################
        #Correct the rotations
        ############################################
        
        self.rotation = round(self.rotation, 2)

        self.rotarray.append(self.rotation)

       
        

        

        self.centre = np.array(self.getcenterCoordinates(fincont))
        print(self.centre)
        self.centarray.append(self.centre)

        self.convertedarray = []
        for center in self.centarray:
            self.converted_coordinates = CoordinateConversion().run(center[0], center[1])
            print(self.converted_coordinates)
            self.convertedarray.append(self.converted_coordinates)

            self.combined_list = list(zip(self.convertedarray, self.rotarray))
            self.combined_list = [[float(center[0]), float(center[1]), float(rot)] for center, rot in self.combined_list]
            

        




     

      
        
        


        label = "  Rotation Angle: " + str((self.rotation))
        textbox = (self.centre[0] - 100, self.centre[1] - 25)
        cv.putText(img, label, textbox, cv.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,255), 1)


        
        
        return self.rotation, self.centre
        #print("Rotation: ", int(self.rotation))
       

    def getVals(self, i):
        testrot = self.rotarray
        testcent = self.convertedarray
        blocks =  self.combined_list
        print("Blocks: ", blocks)
        return blocks[i]

    


if __name__ == "__main__":
    
    main()



    
    


    #cam = Camera()
    #mirror: Detection = MirrorDetect("C:\\Users\\basti\\Pictures\\testimg7.jpg")
    #frame = cam.get_frame()
    #mirror.framegetter(frame)
    #ctrcoords, centercoords = mirror.getCoordinates()
    #print(ctrcoords, centercoords)

    


    
