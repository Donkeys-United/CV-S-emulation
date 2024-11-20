import threading
from CommunicationThread import CommunicationThread
from MessageClasses import Message, RequestMessage, RespondMessage, ResponseNackMessage, ProcessedDataMessage, ImageDataMessage
import socket
from pickle import loads, dumps

class TransmissionThread(threading.Thread):

    HOSTNAME = socket.gethostname()
    IP_ADDR = socket.gethostbyname(HOSTNAME)
    __dataTransmittedBytes = 0

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
        self.__dataTransmittedBytes
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
                        if (isinstance(message, ProcessedDataMessage) == False) and (message.lastSenderID != None):
                            if message.lastSenderID == self.leftSatelliteID:
                                connection.connect(self.rightSatelliteAddr)
                            else:
                                connection.connect(self.leftSatelliteAddr)
                        elif isinstance(message, ProcessedDataMessage):
                            try:
                                connection.connect(self.groundstationAddr)
                            except:
                                if message.lastSenderID == self.leftSatelliteID:
                                    connection.connect(self.rightSatelliteAddr)
                                else:
                                    connection.connect(self.leftSatelliteAddr)
                        
                        message.lastSenderID = self.satelliteID
                        pickled_message = dumps(message)
                        connection.send(pickled_message,)

    def run(self):
        self.sendTransmission()

    def stop(self):
        self._stop_event.set()




