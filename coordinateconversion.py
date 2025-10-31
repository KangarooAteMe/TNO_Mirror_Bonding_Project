import numpy as np
class coordinateconversion:
    def __init__(self): 
       self.camerapixels = {'bottomleft': (0, 736), 
                            'topleft': (0, 0),  
                            'topright': (1076, 0), 
                            'bottomright': (1076, 736)}
       self.robotcoords = {'bottomleft': (-354.24, -573.65),
                          'topleft': (-276.82, -573.65), 
                          'topright': (-276.82, -687.86), 
                          'bottomright': (-354.24, -687.86)}

       self.x_offset = 276.82       
       self.y_offset = 573.65

       self.corfactor = 1 
       self.minioffset = -1

    def convert(self, x, y, facx, facy):

        print(x)
        print(y)
        x_converted = (-y  * (facy * -1) * self.corfactor) + (self.x_offset * -1) 
        y_converted = (-x * (facx * -1) * self.corfactor) + (self.y_offset * -1) 
        print(facx)
        print(facy)
        x_converted = round((x_converted / 1000), 6)
        y_converted = round((y_converted / 1000), 6)

        self.objectpos = (x_converted, y_converted)
        return self.objectpos

    def factorcalculation(self):
        self.scalefactorx = -114.21 / 1080
        self.scalefactory = -77.42 /  730
        return self.scalefactorx , self.scalefactory

   
    
    

    def run(self, x, y):
         facx, facy = self.factorcalculation()
         var = self.convert(x, y, facx, facy)
         return var
        
