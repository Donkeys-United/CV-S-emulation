from abc import ABC
import time


class Message():
    """An abstract class for all the Message classes. Contains no actual functionality.
    """
    pass


class RequestMessage(Message):
    
    def __init__(self, taskID):
        self.unixTimeStamp = time.time()
        self.taskID = taskID
    
    def getUnixTimeStamp(self):
        return self.unixTimeStamp
    
    def getTaskID(self):
        return self.taskID

class RespondMessage(Message):
    pass

class ImageDataMessage(Message):
    pass

class ProcessedDataMessage(Message):
    pass

class ResponseNackMessage(Message):
    pass