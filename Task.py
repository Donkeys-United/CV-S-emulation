from uuid import getnode
from numpy import ndarray
import time

class Task:
    taskID:bytes
    fileName:str
    location:complex
    unixTimestamp:float
    unixTimestampLimit:float
    image:ndarray

    def __init__(self, incrementingID:int, timeLimit:int) -> None:
        self.taskID = getnode().to_bytes(6, 'big') + incrementingID.to_bytes(1, 'big')
        self.unixTimestamp = time.time()
        self.unixTimestampLimit = self.unixTimestamp + timeLimit

    def appendImage(self, fileName:str, image, location:complex) -> None:
        self.fileName = fileName
        self.image = image
        self.location = location
    
    def getTaskId(self) -> int:
        return self.taskID
    
    def getFileName(self) -> str:
        return self.fileName
    
    def getLocation(self) -> complex:
        return self.location
    
    def getUnixTimestamp(self) -> float:
        return self.unixTimestamp
    
    def getUnixTimestampLimit(self) -> float:
        return self.unixTimestampLimit
    
    def getImage(self) -> ndarray:
        return self.image