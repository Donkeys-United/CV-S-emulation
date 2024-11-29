import random, threading, cv2, os
from MessageClasses import *
from Task import Task
from typing import Any, Iterable, List, Mapping, TYPE_CHECKING
import socket
from pickle import loads, dumps


if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from TransmissionThread import TransmissionThread
    from ListeningThread import ListeningThread


class GroundStation(threading.Thread):

    #Change to your prefered directory location for the processed images
    directoryProcessed = "/Users/tobiaslundgaard/Desktop/Semester5"
    directoryUnProcessed = "/Users/tobiaslundgaard/Desktop/Semester5"

    def __init__(self):
        super().__init__()
        

    def saveProcessedImage(self, task: Task):
        """
        Saves the image gotten from the satellites to a specified file location

        Args:
            directory (str): The directory the files should be saved
            image (jpg): The image gotten from the ProcessedImageTask Message
        """
        image = cv2.imread(task.getImage())

        # Change the current directory to specified directory
        os.chdir(self.directoryProcessed)

        #print the location of the directory (just for testing)
        print("Before saving image:", os.listdir(self.directoryProcessed))


        filename = task.getFileName()
        cv2.imwrite(filename, image)
        
        #Print the filename of the image and the location of the directory (just for testing)
        print(f"Image saved as {filename} in the directory {self.directoryProcessed}")


    def saveUnProcessedImage(self, task: Task):
        image = cv2.imread(task.getImage())

        # Change the current directory to specified directory
        os.chdir(self.directoryUnProcessed)

        #print the location of the directory (just for testing)
        print("Before saving image:", os.listdir(self.directoryUnProcessed))


        filename = task.getFileName()
        cv2.imwrite(filename, image)
        
        #Print the filename of the image and the location of the directory (just for testing)
        print(f"Image saved as {filename} in the directory {self.directoryUnProcessed}")


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
    LISTENING_PORT: int = 4500
    TRANSMISSION_PORT: int = 4600
  
    def __init__(self):
        super().__init__()

        self.transmissionThread: TransmissionThread = TransmissionThread()
        self.listeningThreadLeft = ListeningThread(port=self.LISTENING_PORT, communicationThread=self)
        self.listeningThreadLeft.start()
        self.transmissionThread.start()
        

        
    def run():
        pass


class ListeningThread(threading.Thread):
    """Class for Listening Thread. Used for listening on a specific port for incoming messages.
    """
    HOSTNAME = socket.gethostname()
    IP_ADDR = socket.gethostbyname(HOSTNAME)

    def __init__(self, port: int, communicationThread: CommunicationThread):
        super().__init__()
        self.port = port
        self.communicationThread = communicationThread
        self._stop_event = threading.Event()
        self.HOSTNAME
        self.IP_ADDR
        self.counter = 0
    
    def activeListening(self):
        """Method for making the thread listen to the specific port.
        """
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection.bind((self.IP_ADDR, self.port))
        while not self._stop_event.is_set():
            connection.listen()
            incoming_message = connection.accept()
            unpickled_message = loads(incoming_message)
            if unpickled_message == isinstance(unpickled_message, RequestMessage):
                   GroundStation.sendRespond()
                   GroundStation.saveUnProcessedImage(unpickled_message)
                   self.counter += 1   
            elif unpickled_message == isinstance(unpickled_message, ImageDataMessage):
                #Add try except later
                GroundStation.saveProcessedImage(unpickled_message)
                print("Filed saved")
            else:
                pass

    def run(self):
        self.activeListening()

    def stop(self):
        self._stop_event.set()


class TransmissionThread(threading.Thread):
    """Class for creating the transmission thread.
    """

    HOSTNAME = socket.gethostname()
    IP_ADDR = socket.gethostbyname(HOSTNAME)
    port = 6969 # Port selected for outgoing comms.


    def __init__(self, port: int, communicationThread: CommunicationThread):
        super().__init__()
        self.communicationThread = communicationThread
        self._stop_event = threading.Event()
        self.HOSTNAME
        self.IP_ADDR
        
        
    def sendTransmission(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.bind((self.IP_ADDR, self.port))

            while not self._stop_event.is_set():
                pass