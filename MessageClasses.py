from abc import ABC
import time
import Task


class Message():
    """An abstract class for all the Message classes. Contains no actual functionality.
    """
    pass


class RequestMessage(Message):
    
    def __init__(self, unixTimeLimit: float, taskID: int):
        self.__unixTimeLimit__ = unixTimeLimit
        self.__taskID__ = taskID
    
    def getUnixTimeStamp(self):
        return self.__unixTimeLimit__
    
    def getTaskID(self):
        return self.__taskID__

class RespondMessage(Message):

    def __init__(self, taskID: int, MAC: int):
        self.__source__ = MAC
        self.__taskID__ = taskID
    
    def getTaskID(self):
        return self.__taskID__
    
    def getSource(self):
        return self.__source__

class ImageDataMessage(Message):
    
    def __init__(self, payload: Task):
        self.__payload__ = payload

    def getPayload(self):
        return self.__payload__

class ProcessedDataMessage(Message):
    pass

class ResponseNackMessage(Message):
    
    def __init__(self, taskID: int):
        self.__taskID__ = taskID
    
    def getTaskID(self):
        return self.__taskID__