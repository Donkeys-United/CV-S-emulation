import random
import threading
import cv2
import os
from MessageClasses import *
from Task import Task
from typing import TYPE_CHECKING
import socket
from pickle import loads, dumps

if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from TransmissionThread import TransmissionThread
    from ListeningThread import ListeningThread


class GroundStation:
    
    #Change to your prefered directory location for the processed images and unprocessed images
    directoryProcessed = "/Users/tobiaslundgaard/Desktop/Semester5"
    directoryUnProcessed = "/Users/tobiaslundgaard/Desktop/Semester5"

    def __init__(self):
        self.transmissionThread = None

    def saveProcessedImage(self, task: Task):
        image = cv2.imread(task.getImage())
        os.chdir(self.directoryProcessed)
        filename = task.getFileName()
        cv2.imwrite(filename, image)
        print(f"Processed image saved as {filename}")

    def saveUnProcessedImage(self, task: Task):
        image = cv2.imread(task.getImage())
        os.chdir(self.directoryUnProcessed)
        filename = task.getFileName()
        cv2.imwrite(filename, image)
        print(f"Unprocessed image saved as {filename}")

    def sendRespond(self, task: Task, message: Message):
        respond_message = RespondMessage(
            taskID=task.getTaskID(),
            source=task.getSource(),
            firstHopID=message.lastSenderID
        )
        self.transmissionThread.sendTransmission(respond_message)


class CommunicationThread(threading.Thread):
    LISTENING_PORT = 4500
    TRANSMISSION_PORT = 4600

    def __init__(self):
        super().__init__()
        self.groundStation = GroundStation()
        self.transmissionThread = TransmissionThread(port=self.TRANSMISSION_PORT, communicationThread=self)
        self.listeningThread = ListeningThread(port=self.LISTENING_PORT, communicationThread=self, groundStation=self.groundStation)

    def run(self):
        print("CommunicationThread started")
        self.listeningThread.start()
        print("ListeningThread started from CommunicationThread")
        self.transmissionThread.start()
        print("TransmissionThread started from CommunicationThread")


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
                data, _ = self.connection.recvfrom(4096)
                message = loads(data)
                if isinstance(message, RequestMessage):
                    self.groundStation.sendRespond(message.task, message)
                    self.groundStation.saveUnProcessedImage(message.task)
                elif isinstance(message, ImageDataMessage):
                    self.groundStation.saveProcessedImage(message.task)
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
            pass  

    def stop(self):
        self._stop_event.set()


if __name__ == "__main__":
    comm_thread = CommunicationThread()
    comm_thread.start()
