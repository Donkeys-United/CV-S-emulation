import random
import threading
import cv2
import os
from MessageClasses import *
from Task import Task
from typing import TYPE_CHECKING
import socket
from pickle import loads, dumps
import uuid

if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from TransmissionThread import TransmissionThread
    from ListeningThread import ListeningThread


class GroundStation():
    directoryProcessed = "/Users/tobiaslundgaard/Desktop/Semester 5/Projekt5/Processed/"
    directoryUnProcessed = "/Users/tobiaslundgaard/Desktop/Semester 5/Projekt5/UnProcessed"
    
    def __init__(self, transmissionThread: 'TransmissionThread'):
        # Make sure transmissionThread is set during initialization
        self.transmissionThread = transmissionThread


    def saveProcessedImage(self, message: ProcessedDataMessage):

        """
        Mangler at fikse og teste med ProcessedDataMessage pakke, og fikse logik
        """
        payload = message.getPayload()
        # Get the full file name (with the directory)
        filename = payload.getFileName()

        # Load the image using the full path (filename includes full path)
        image = cv2.imread(filename)
        if image is None:
            print(f"Error loading image: {payload.getImage()}")
        else:
            print(f"Image loaded successfully: {payload.getImage()}")
        
        # Extract the file name from the full path (remove the directory)
        base_filename = os.path.basename(filename)    
        # Construct the full save path by joining the target directory and the base filename
        save_path = os.path.join(self.directoryProcessed, base_filename)
        cv2.imwrite(save_path, image)
        print(f"Unprocessed image saved as {save_path}")

    def saveUnProcessedImage(self, message: ImageDataMessage):
        payload = message.getPayload()
        # Get the full file name (with the directory)
        filename = payload.getFileName()
        # Load the image using the full path (filename includes full path)
        image = cv2.imread(filename)
        if image is None:
            print(f"Error loading image: {payload.getImage()}")
        else:
            print(f"Image loaded successfully: {payload.getImage()}")
        
        # Extract the file name from the full path (remove the directory)
        base_filename = os.path.basename(filename)
        
        # Construct the full save path by joining the target directory and the base filename
        save_path = os.path.join(self.directoryUnProcessed, base_filename)
        
        # Print the save path for debugging
        print(f"Saving image as: {save_path}")
        
        # Save the image to the target directory
        cv2.imwrite(save_path, image)
        print(f"Unprocessed image saved as {save_path}")



    def sendRespond(self, message: RequestMessage):
        print("I AM HERE")
        respond_message = RespondMessage(
            taskID = message.getTaskID(),  # Corrected method usage
            source = uuid.getnode(),
            firstHopID = message.lastSenderID
        )
        print("I AM HERE2")
        if self.transmissionThread:
            print("I AM HERE3")
            self.transmissionThread.sendTransmission(respond_message)
            print(self.transmissionThread.sendTransmission(respond_message))
            print("I AM HERE4")
        else:
            print("Error: transmissionThread is not initialized.")
            print("I AM HERE5")


class CommunicationThread(threading.Thread):
    LISTENING_PORT = 4500
    TRANSMISSION_PORT = 4600

    def __init__(self):
        super().__init__()
        self.transmissionThread = TransmissionThread(port=self.TRANSMISSION_PORT, communicationThread=self)
        self.groundStation = GroundStation(transmissionThread=self.transmissionThread)  # Pass transmissionThread
        self.listeningThread = ListeningThread(port=self.LISTENING_PORT, communicationThread=self, groundStation=self.groundStation)

    def run(self):
        # Start both threads
        self.listeningThread.start()
        self.transmissionThread.start()


class ListeningThread(threading.Thread):
    def __init__(self, port: int, communicationThread: CommunicationThread, groundStation: GroundStation):
        super().__init__()
        self.port = port
        self.communicationThread = communicationThread
        self.groundStation = groundStation
        self._stop_event = threading.Event()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.connection.bind((socket.gethostname(), self.port))

    def activeListening(self):
        while not self._stop_event.is_set():
            try:
                data, _ = self.connection.recvfrom(100000)
                message = loads(data)
                print(f"Received message: {message}")
                if isinstance(message, RequestMessage):
                    self.groundStation.sendRespond(message)
                elif isinstance(message, ImageDataMessage):
                    self.groundStation.saveUnProcessedImage(message)
                elif isinstance(message, ProcessedDataMessage):
                    self.groundStation.saveProcessedImage(message)
                else:
                    print("Unknown message received.")
            except Exception as e:
                print(f"Error in listening thread: {e}")

    def run(self):
        self.activeListening()

    def stop(self):
        self._stop_event.set()


class TransmissionThread(threading.Thread):
    def __init__(self, port: int, communicationThread: CommunicationThread):
        super().__init__()
        self.port = port
        self.communicationThread = communicationThread
        self._stop_event = threading.Event()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def sendTransmission(self, message):
        try:
            self.connection.sendto(dumps(message), (socket.gethostname(), self.port))
        except Exception as e:
            print(f"Error in transmission: {e}")

    def run(self):
        while not self._stop_event.is_set():
            pass  # Placeholder for future logic

    def stop(self):
        pass
        #self._stop_event.set()


if __name__ == "__main__":
    print("Starting CommunicationThread...")
    comm_thread = CommunicationThread()
    comm_thread.start()
    print("CommunicationThread has been started")
