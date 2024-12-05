import threading
from MessageClasses import Message, RequestMessage, RespondMessage, ResponseNackMessage, ProcessedDataMessage, ImageDataMessage
import socket
from pickle import dumps
from uuid import getnode
import struct
from getmac import get_mac_address
import time

class TransmissionThread(threading.Thread):
    """Class for creating the transmission thread.
    """
    from CommunicationThread import CommunicationThread

    HOSTNAME = socket.gethostname()
    #IP_ADDR = socket.gethostbyname(HOSTNAME)
    IP_ADDR = "0.0.0.0"
    __dataTransmittedBytes = 0 # Used for power consumption optimization.
    port = 6969 # Port selected for outgoing comms.
    __satelliteID = int(get_mac_address("usb0").replace(":",""),16) # MAC Address



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
        self.leftSatelliteAddr = (neighbourSatelliteAddrs[0], 4500)
        self.rightSatelliteAddr = (neighbourSatelliteAddrs[1],4600)
        self.groundstationAddr = groundstationAddr



    def getDataTransmitted(self):
        """Method for reading the value of the __dataTransmittedBytes attribute.

        Returns:
            int: number of bytes transmitted.
        """

        return self.__dataTransmittedBytes



    def sendTransmission(self):
        #with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
        #with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
            #connection.bind((self.IP_ADDR, self.port))

        while not self._stop_event.is_set():
            if self.communicationThread.transmissionQueue:
                message = self.communicationThread.transmissionQueue.pop(0)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
                    #connection.bind((self.IP_ADDR, self.port))
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
                                    print(f"\nSending message to left satellite with address {self.leftSatelliteAddr}")
                                    connection.connect(self.leftSatelliteAddr)

                                else:
                                    print(f"\nSending message to right satellite with address {self.rightSatelliteAddr}")
                                    connection.connect(self.rightSatelliteAddr)


                        # Case 4: The satellite sends out its own RequestMessage - which must be sent to both neighbouring satellites.
                        elif isinstance(message, RequestMessage):
                            message.lastSenderID = self.__satelliteID
                            pickled_message = dumps(message)
                            self.__dataTransmittedBytes += len(pickled_message)
                            message_length = len(pickled_message)
                            header = struct.pack('>I', message_length)

                            connection.connect(self.rightSatelliteAddr)
                            connection.sendall(header + pickled_message)

                            time.sleep(2)

                            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection_2:
                                connection_2.connect(self.leftSatelliteAddr)
                                connection_2.sendall(header + pickled_message)
                                print(f"Sent request message\n")
                                connection_2.shutdown(socket.SHUT_RDWR)
                                connection_2.close()


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
                        message_length = len(pickled_message)
                        header = struct.pack('>I', message_length)
                        connection.sendall(header + pickled_message)
                        #print(f"\n\n\nTransmission Queue:{self.communicationThread.transmissionQueue}\n\n\n")
                        print(f"Sent image: {message.getFileName()}\n")
                        connection.shutdown(socket.SHUT_RDWR)
                        connection.close()



    def run(self):
        self.sendTransmission()



    def stop(self):
        self._stop_event.set()

