import Task
from cv2 import imread


class Message():
    """An abstract class for all the Message classes. Contains no actual 
       functionality.
    """
    pass



class RequestMessage(Message):
    """Class for sending a request to other satellites, requesting that they '
       process the data.
    """

    def __init__(self, unixTimeLimit: float, taskID: int):
        self.__unixTimeLimit__ = unixTimeLimit
        self.__taskID__ = taskID


    def getUnixTimeLimit(self):
        """Method for returning the __unixTimeLimit__ attribute value.

        Returns:
            float: the unix time limit, meaning the unix time stamp + the 
                   time limit for the processing.
        """

        return self.__unixTimeLimit__


    def getTaskID(self):
        """Method for returning the __taskID__ attribute value.

        Returns:
            int: the taskID which is a number for the unique task plus the MAC address of the original satellite.
        """

        return self.__taskID__



class RespondMessage(Message):
    """Class for sending an ack response to a satellite, when receiving a 
       RequestMessage, and accepting the task.
    """

    def __init__(self, taskID: int, MAC: int):
        self.__source__ = MAC
        self.__taskID__ = taskID


    def getTaskID(self):
        """Method for returning the __taskID__ attribute value.

        Returns:
            int: the taskID which is a number for the unique task plus the
                 MAC address of the original satellite.
        """

        return self.__taskID__


    def getSource(self):
        """Method for returning the __source__ attribute value.

        Returns:
            int: the MAC address of the responding satellite.
        """

        return self.__source__



class ImageDataMessage(Message):

    def __init__(self, payload: Task):
        self.__payload__ = payload



    def getPayload(self):
        """Method for returning the __payload__ attribute value.

        Returns:
            Task: the Task object instance.
        """

        return self.__payload__



class ProcessedDataMessage(Message):
    """Class for creating messages with the results from the
       ObjectDetectionThread. They are meant to be sent to the ground station.
    """

    def __init__(self, 
                 image: str, 
                 location: complex, 
                 unixTimeStamp: float, 
                 fileName: str, 
                 boundingBox: tuple):
        self.__image__ = imread(image)
        self.__location__ = location
        self.__unixTimeStamp__ = unixTimeStamp
        self.__fileName__ = fileName
        self.__boundingBox__ = boundingBox


    def getImage(self):
        """Method for returning the __image__ attribute value.

        Returns:
            numpy.ndarray: the processed image, processed by the 
                           ObjectDetectionThread.
        """

        return self.__image__


    def getLocation(self):
        """Method for returning the __location__ attribute value.

        Returns:
            complex: satellites location written as a complex number.
        """

        return self.__location__


    def getUnixTimeStamp(self):
        """Method for returning the __unixTimeStamp__ attribute value.

        Returns:
            float: unix time stamp for when the image was "captured".
        """

        return self.__unixTimeStamp__


    def getFileName(self):
        """Method for returning the __fileName__ attribute value.

        Returns:
            str: file name of the original image file. Used by the ground
                 station for determining IoU.
        """

        return self.__location__


    def getBoundingBox(self):
        """Method for returning the __boundingBox__ attribute value.

        Returns:
            tuple: tuple containing 2 tuples. Each nested tuple has a set of 
                   xy coordinates, for the location of the bounding box.
        """

        return self.__boundingBox__



class ResponseNackMessage(Message):
    """Class for sending a Nack to a responding satellite, it not sending the
       task to that satellite.
    """

    def __init__(self, taskID: int):
        self.__taskID__ = taskID


    def getTaskID(self):
        """Method for returning the __taskID__ attribute value.

        Returns:
            int: the taskID which is a number for the unique task plus the MAC address of the original satellite.
        """

        return self.__taskID__