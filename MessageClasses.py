import time
from abc import ABC, abstractmethod
from typing import Tuple

#Abstract class
class Message():

    @abstractmethod
    def __init__(self):
        pass

class RequestMessage(Message):
    def __init__(self, unix_time_limit: int, task_id: str):
        super().__init__()
        self.unix_time_limit = unix_time_limit
        self.task_id = task_id

    def getUnixTimeLimit(self) -> int:
        return self.unix_time_limit

    def getTaskID(self) -> str:
        return self.task_id


class RespondMessage(Message):
    def __init__(self, task_id: str, source: str):
        self.task_id = task_id
        self.source = source

    def getTaskID(self) -> str:
        return self.task_id

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

    def get_payload(self):
        return self.taskID, self.fileName, self.location, self.image, self.unixTimestamp, self.unixTimestampLimit

class ProcessedDataMessage(Message):
    def __init__(self, image: 'jpg', location: complex, unix_timestamp: int, file_name: str, bounding_box: Tuple[Tuple[int, int], Tuple[int, int]]):
        self.image = image
        self.location = location
        self.unix_timestamp = unix_timestamp
        self.file_name = file_name
        self.bounding_box = bounding_box

    def get_image(self):
        return self.image

    def get_location(self) -> complex:
        return self.location

    def get_unix_timestamp(self) -> int:
        return self.unix_timestamp

    def get_file_name(self) -> str:
        return self.file_name

class ResponseNackMessage(Message):
    def __init__(self, task_id: str):
        self.task_id = task_id

    def get_task_id(self) -> str:
        return self.task_id
