import threading
from MessageClasses import Message, RequestMessage, RespondMessage, ResponseNackMessage, ProcessedDataMessage, ImageDataMessage
import socket
from pickle import dumps
from uuid import getnode

class TransmissionThread(threading.Thread):
    """Class for creating the transmission thread.
    """
    from CommunicationThread import CommunicationThread

    HOSTNAME = socket.gethostname()
    IP_ADDR = socket.gethostbyname(HOSTNAME)
    __dataTransmittedBytes = 0 # Used for power consumption optimization.
    port = 6969 # Port selected for outgoing comms.
    __satelliteID = getnode() # MAC Address



    def __init__(self, 
                 communicationThread: CommunicationThread, 
                 neighbourSatelliteIDs: tuple, 
                 neighbourSatelliteAddrs: tuple,
                 groundstationAddr: tuple):
        """Initialization of TransmissionThread.

        Args:
            communicationThread (CommunicationThread): CommunicationThread object instance, used as the reference to interact with the specific communication thread.

            neighbourSatelliteIDs (tuple): tuple of (MAC address, MAC address), which contains the MAC addresses of the neighbouring satellites. It should be written as (left satellite, right satellite).

            neighbourSatelliteAddrs (tuple): tuple of (IP address, IP address), which contains the IP address of the neighbouring satellites. It should be written as (left satellite, right satellite).

            groundstationAddr (tuple): IP address of the ground station.
        """

        super().__init__()
        self.port
        self.communicationThread = communicationThread
        self._stop_event = threading.Event() # Used for stopping the thread.
        self.HOSTNAME
        self.IP_ADDR
        self.__dataTransmittedBytes
        self.__satelliteID
        self.leftSatelliteID = neighbourSatelliteIDs[0]
        self.rightSatelliteID = neighbourSatelliteIDs[1]
        self.leftSatelliteAddr = neighbourSatelliteAddrs[0]
        self.rightSatelliteAddr = neighbourSatelliteAddrs[1]
        self.groundstationAddr = groundstationAddr



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



    def run(self):
        self.sendTransmission()



    def stop(self):
        self._stop_event.set()

