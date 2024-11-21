import time
from abc import ABC, abstractmethod
from typing import Tuple

#Abstract class
class Message():

    @abstractmethod
    def __init__(self):
        pass

class RequestMessage(Message):
    def __init__(self, unixTimeLimit: float, taskID: int):
        super().__init__()
        self.unixTimeLimit = unixTimeLimit
        self.taskID = taskID

    def getUnixTimeLimit(self) -> float:
        return self.unixTimeLimit

    def getTaskID(self) -> int:
        return self.taskID
    
    def __str__(self):
        return f"RequestMessage(taskID={self.taskID}, unixTimeLimit={self.unixTimeLimit})"


class RespondMessage(Message):
    def __init__(self, taskID: str, source: str):
        self.taskID = taskID
        self.source = source

    def getTaskID(self) -> str:
        return self.taskID

    def getSource(self) -> str:
        return self.source

class ImageDataMessage(Message):
    def __init__(self, taskID: int, fileName: str, location: complex, unixTimestamp: float, unixTimestampLimit: float, image: 'jpg'):
        self.taskID = taskID
        self.fileName = fileName
        self.location = location
        self.image = image
        self.unixTimestamp = unixTimestamp
        self.unixTimestampLimit = unixTimestampLimit

    def getPayload(self):
        return self.taskID, self.fileName, self.location, self.image, self.unixTimestamp, self.unixTimestampLimit

class ProcessedDataMessage(Message):
    def __init__(self, image: 'jpg', location: complex, unixTimestamp: int, fileName: str, boundingBox: Tuple[Tuple[int, int], Tuple[int, int]]):
        self.image = image
        self.location = location
        self.unixTimestamp = unixTimestamp
        self.fileName = fileName
        self.boundingBox = boundingBox

    def getImage(self):
        return self.image

    def getLocation(self) -> complex:
        return self.location

    def getUnixTimestamp(self) -> int:
        return self.unixTimestamp

    def getFileName(self) -> str:
        return self.fileName

class ResponseNackMessage(Message):
    def __init__(self, taskID: str):
        self.taskID = taskID

    def getTaskID(self) -> str:
        return self.taskID
