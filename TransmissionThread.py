import threading
from CommunicationThread import CommunicationThread
from MessageClasses import Message, RequestMessage, RespondMessage, ResponseNackMessage, ProcessedDataMessage, ImageDataMessage
import socket
from pickle import dumps

class TransmissionThread(threading.Thread):

    HOSTNAME = socket.gethostname()
    IP_ADDR = socket.gethostbyname(HOSTNAME)
    dataTransmittedBytes = 0

    def __init__(self, 
                 port: int, 
                 communicationThread: CommunicationThread, satelliteID: int, 
                 neighbourSatelliteIDs: tuple, 
                 neighbourSatelliteAddrs: tuple,
                 groundstationAddr: tuple):
        super().__init__()
        self.port = port
        self.communicationThread = communicationThread
        self._stop_event = threading.Event()
        self.HOSTNAME
        self.IP_ADDR
        self.dataTransmittedBytes
        self.satelliteID = satelliteID
        self.leftSatelliteID = neighbourSatelliteIDs[0]
        self.rightSatelliteID = neighbourSatelliteIDs[1]
        self.leftSatelliteAddr = neighbourSatelliteAddrs[0]
        self.rightSatelliteAddr = neighbourSatelliteAddrs[1]
        self.groundstationAddr = groundstationAddr
    
    def getDataTransmitted(self):
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
                            message.lastSenderID = self.satelliteID
                            pickled_message = dumps(message)
                            self.dataTransmittedBytes += len(pickled_message)

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

                        message.lastSenderID = self.satelliteID
                        pickled_message = dumps(message)
                        self.dataTransmittedBytes += len(pickled_message)
                        connection.send(pickled_message)
                        connection.shutdown()

    def run(self):
        self.sendTransmission()

    def stop(self):
        self._stop_event.set()




