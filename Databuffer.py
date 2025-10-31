from detection import detection

class databuffer:
    def __init__(self, mirror, block):
        self.mir = mirror
        self.blk = block
        self.arrayify = []
        self.bl = 0
        self.mi = 0


    def collectVisData(self):    

        datablk = self.blk.getVals(self.bl)
        
        if self.bl < len(self.blk.blocks):
            
            self.bl = self.bl + 1
            return datablk
        else:
            return None

    def collectfinalPos(self):    

        pos = self.mir.getVals(self.mi)
        
        if self.mi < len(self.mir.mirrordata):
            
            self.mi = self.mi + 1
            return pos
        else:
            return None
