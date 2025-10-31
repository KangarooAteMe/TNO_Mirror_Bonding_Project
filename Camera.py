
from state_enum import program_State
from Network_client import Network_client

import cv2 as cv
import os
from harvesters.core import Harvester
import time
class camera:
    def __init__(self):
        
        self.state = program_State.IDLE
        self.camnum = 0
        self.current_state = program_State.IDLE


    def update_state(self, new_state):
            if new_state != self.current_state:
                self.previous_state = self.current_state
                self.current_state = new_state
                return self.current_state

            print(f"current state: {self.current_state}")
            print(f"State changed from {self.previous_state} to {self.current_state}")

            
        
    def run(self, state):
           
                self.state = state

                if  self.state is None:
                    Exception("Trigger is None")
                    self.state = self.update_state(program_State.IDLE)

                elif self.state == "error":
                    self.state = self.update_state(program_State.ERROR)

                elif self.state== "Cheese":
                    self.state = self.update_state(program_State.GET_BLOCK_COORDS)
                    

                elif self.state == "prep_glue_dispense_1":
                    self.state = self.update_state(program_State.PREP_GLUE_1)
                    msg = "glue_prep_1_busy"
                    time.sleep(5)
                    msg = "glue_prep_1_done"

                elif self.state == "prep_glue_dispense_2":
                    self.state = self.update_state(program_State.PREP_GLUE_2)
                    msg = "glue_prep_2_busy"
                    time.sleep(5)
                    msg = "glue_prep_2_done"

                elif self.state == "Block":
                    msg = "mirror_capture_busy"
                    self.state = self.update_state(program_State.GET_FINAL_COORDS)

               
                return self.state

               





    def harvest(self):
        direc = r"C:\Users\basti\Pictures\ims\protoimages"
        if self.camnum == 0:
            CTI_FILE_PATH = "C:/Program Files/Daheng Imaging/GalaxySDK/GenTL/Win64/GxGVTL.cti"  # The filepath to the CTI file
           # Create a Harvester instance
            h = Harvester()
            
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
                    cv.imwrite(os.path.join(direc, "BlockCap.bmp"), img)
        else:
            cap = cv.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                cv.imwrite(os.path.join(direc, "MirrorCap.bmp"), frame)
            cap.release()
            if not ret:
                print("Failed to capture image from camera.")
                

    
    def switch_camera(self):
        if self.camnum == 0:
            self.camnum = 1
        else:
            self.camnum = 0



