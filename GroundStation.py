import random, threading, cv2, os
from MessageClasses import *
from Task import Task
from typing import Any, Iterable, List, Mapping, TYPE_CHECKING


if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from TransmissionThread import TransmissionThread
    from ListeningThread import ListeningThread


class GroundStation(threading.Thread):

    directory = "/Users/tobiaslundgaard/Desktop/Semester5"

    def __init__(self):
        super().__init__()
        

    def saveImage(self, task: Task):
        """
        Saves the image gotten from the satellites to a specified file location

        Args:
            directory (str): The directory the files should be saved
            image (jpg): The image gotten from the ProcessedImageTask Message
        """

        image = cv2.imread(task.getImage())

        # Change the current directory to specified directory
        os.chdir(self.directory)

        #print the location of the directory
        print("Before saving image:", os.listdir(self.directory))


        filename = task.getFileName()
        cv2.imwrite(filename, image)
        print(f"Image saved as {filename} in the directory {self.directory}")





    def sendRespond(self, task: Task, message: Message):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        sendRespondMessage = RespondMessage(
            taskID=task.getTaskID(),
            source=task.getSource(),
            firstHopID = message.lastSenderID
        )

        self.communicationThread.addTransmission(sendRespondMessage)


class CommunicationThread(threading.Thread):

    #Constants 
    LISTENING_PORT: int 


  
    def __init__(self, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: random.Iterable[random.Any] = ..., kwargs: threading.Mapping[str, random.Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

        self.transmissionThread: TransmissionThread = TransmissionThread()
        

        
    def run():
        pass



class TransmissionThreadGS(threading.Thread):
    """Class for creating the GS's transmission thread 
    """

    def __init__(self, communicationThread: CommunicationThread, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)


    def getDataTransmitted(self):
        """Method for reading the value of the __dataTransmittedBytes attribute.

        Returns:
            int: number of bytes transmitted.
        """

        return self.__dataTransmittedBytes
    
    
    
    def sendTransmission(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.bind((self.IP_ADDR, self.port))

            while not self._stop_event.is_set():
                if self.communicationThread.transmissionQueue:
                    message = self.communicationThread.transmissionQueue.pop(0)
                    if isinstance(message, Message):

                        # Case 1: The satellite must relay a message to the next satellite in the chain.
                        if (isinstance(message, ProcessedDataMessage) == False) and (message.lastSenderID != None):
                            if message.lastSenderID == self.leftSatelliteID:
                                connection.connect(self.rightSatelliteAddr)
                            else:
                                connection.connect(self.leftSatelliteAddr)

                        # Case 2: The satellite must relay the result message to either the groundstation or the next satellite.
                        elif isinstance(message, ProcessedDataMessage) and (message.lastSenderID != None):
                            try:
                                connection.connect(self.groundstationAddr)
                            except:
                                if message.lastSenderID == self.leftSatelliteID:
                                    connection.connect(self.rightSatelliteAddr)
                                else:
                                    connection.connect(self.leftSatelliteAddr)

                        # Case 3: The satellite must send its own results to the groundstation, or another satellite.
                        elif isinstance(message, ProcessedDataMessage):
                            try:
                                connection.connect(self.groundstationAddr)
                            except:
                                if message.firstHopID == self.leftSatelliteID:
                                    connection.connect(self.rightSatelliteAddr)
                                else:
                                    connection.connect(self.leftSatelliteAddr)

                        # Case 4: The satellite sends out its own RequestMessage - which must be sent to both neighbouring satellites.
                        elif isinstance(message, RequestMessage):
                            message.lastSenderID = self.__satelliteID
                            pickled_message = dumps(message)
                            self.__dataTransmittedBytes += len(pickled_message)

                            connection.connect(self.rightSatelliteAddr)
                            connection.send(pickled_message)
                            connection.shutdown()

                            connection.connect(self.leftSatelliteAddr)
                            connection.send(pickled_message)
                            connection.shutdown()

                            continue

                        # Case 5: The satellite sends any other message created by itself to one of its neighbouring satellites.
                        else:
                            if message.firstHopID == self.leftSatelliteID:
                                connection.connect(self.rightSatelliteAddr)
                            else:
                                connection.connect(self.leftSatelliteAddr)

                        message.lastSenderID = self.__satelliteID
                        pickled_message = dumps(message)
                        self.__dataTransmittedBytes += len(pickled_message)
                        connection.send(pickled_message)
                        connection.shutdown()




