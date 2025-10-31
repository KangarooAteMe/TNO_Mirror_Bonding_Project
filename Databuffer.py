from detection import detection

class Databuffer:
    def __init__(self, mirror, block):
        self.mir = mirror
        self.blk = block
        self.arrayify = []

    def collectVisData(self):

        self.datablk = self.blk.getVals()
        self.datamir = self.mir.getVals()
        self.arrayify.append(self.datablk)
        self.arrayify.append(self.datamir) ### not send correctly yet
        print(self.arrayify) 
