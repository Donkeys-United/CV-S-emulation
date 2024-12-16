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
import struct
import torch

if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from TransmissionThread import TransmissionThread
    from ListeningThread import ListeningThread


class GroundStation():
    directoryProcessed = "/Users/tobiaslundgaard/Desktop/Semester 5/Projekt5/Processed/"
    directoryUnProcessed = "/Users/tobiaslundgaard/Desktop/Semester 5/Projekt5/UnProcessed"
    processedCounter = 0
    unProcessedCounter = 0
    
    def __init__(self, transmissionThread: 'TransmissionThread'):
        # Make sure transmissionThread is set during initialization
        self.transmissionThread = transmissionThread


    def saveProcessedImage(self, message: ProcessedDataMessage):
        image = message.getImage()
        #print(image)
        # Get the full file name (with the directory)
        filename = message.getFileName()
        lastSender = message.lastSenderID
        print(f"lastSenderID is {lastSender}")
        if image is None:
            print(f"Error loading image: {message.getImage()}")
        else:
            print("Image loaded successfully")
            self.processedCounter += 1
            print(self.processedCounter)
        
        # Extract the file name from the full path (remove the directory)
        base_filename = os.path.basename(filename)    
        # Construct the full save path by joining the target directory and the base filename
        save_path = os.path.join(self.directoryProcessed, base_filename)
        cv2.imwrite(save_path, image)
        print(f"Processed image saved as {save_path}")

    def saveUnProcessedImage(self, message: ImageDataMessage):
        
        payload = message.getPayload()
        image = payload.getImage()
        # Get the full file name (with the directory)
        filename = payload.getFileName()
        if image is None:
            print(f"Error loading image: {payload.getImage()}")
        else:
            print("Image loaded successfully")
            self.unProcessedCounter += 1
            print(self.unProcessedCounter)
        
        # Extract the file name from the full path (remove the directory)
        base_filename = os.path.basename(filename)
        
        # Construct the full save path by joining the target directory and the base filename
        save_path = os.path.join(self.directoryUnProcessed, base_filename)
        
        # Print the save path for debugging
        print(f"Saving image as: {save_path}")
        
        # Save the image to the target directory
        cv2.imwrite(save_path, image)
        print(f"Unprocessed image saved as {save_path}")



    def sendRespond(self, message: RequestMessage, addr):
        print(f"Requestmessage received from {message.getTaskID()}")
        recipient = int.from_bytes(message.getTaskID(), "big") & 0x0000FFFFFFFFFFFF
        respond_message = RespondMessage(
            taskID = message.getTaskID(),  # Corrected method usage
            source = "GROUND",
            firstHopID = message.lastSenderID,
            recipient=recipient
        )
        
        if self.transmissionThread:
            self.transmissionThread.sendTransmission(respond_message, addr)
            print(self.transmissionThread.sendTransmission(respond_message, addr))
        else:
            print("Error: transmissionThread is not initialized.")



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
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.bind(("192.168.0.101", self.port))

    def activeListening(self):
        while not self._stop_event.is_set():
            try:
                self.connection.listen()
                socket, addr = self.connection.accept()
                # Receive the length prefix
                length_prefix = socket.recv(4)
                if not length_prefix:
                    print("Connection closed or no data received.")
                    continue
                # Unpack the length prefix to get the message size
                data_length = struct.unpack('!I', length_prefix)[0]

                # Receive the entire message based on the length
                received_data = b""
                while len(received_data) < data_length:
                    chunk = socket.recv(1024)  # Read in chunks
                    if not chunk:
                        break
                    received_data += chunk
                #data = socket.recv(64000)

                message = loads(received_data)
                if isinstance(message, RequestMessage):
                    self.groundStation.sendRespond(message, addr)
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
        
        

    def sendTransmission(self, message, addr):
        print(addr)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            try:
                pickled_message = dumps(message)
                message_length = len(pickled_message)
                header = struct.pack('>I', message_length)
                final_message = header + pickled_message
                final_addr = (addr[0], 4600)
                connection.connect(final_addr)
                connection.sendall(final_message)
                connection.close()
            except Exception as e:
                print(f"Error in transmission: {e}")

    def run(self):
        while not self._stop_event.is_set():
            pass



if __name__ == "__main__":
    print("Starting CommunicationThread...")
    comm_thread = CommunicationThread()
    comm_thread.start()
    print("CommunicationThread has been started")
