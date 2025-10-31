from abc import ABC, abstractmethod


class Detection(ABC) :
    @abstractmethod
    def findContour(self) :
        pass

    @abstractmethod
    def getCoordinates(self) :
        pass
    @abstractmethod
    def framegetter(self, frame):
        pass

    @abstractmethod
    def getOrientation(self):
        pass

    @abstractmethod
    def getVals():
        pass
    
