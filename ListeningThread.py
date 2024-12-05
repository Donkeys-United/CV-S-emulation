import threading
from MessageClasses import Message
import socket
from pickle import loads
import struct

class ListeningThread(threading.Thread):
    """Class for Listening Thread. Used for listening on a specific port for incoming messages.
    """
    from CommunicationThread import CommunicationThread
    HOSTNAME = socket.gethostname()
    IP_ADDR = "0.0.0.0"

    def __init__(self, port: int, communicationThread: CommunicationThread):
        
        super().__init__()
        self.port = port
        self.communicationThread = communicationThread
        self._stop_event = threading.Event()
        self.HOSTNAME
        self.IP_ADDR
    
    def addMessageList(self, message: Message):
        """Adds an incoming messages to the message list in the communication thread.

        Args:
            message (Message): the incoming message.
        """

        self.communicationThread.messageList.append(message)
    
    def activeListening(self):
        """Method for making the thread listen to the specific port.
        """

        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.bind((self.IP_ADDR, self.port))
        while not self._stop_event.is_set():
            connection.listen()
            sock, addr = connection.accept()
            length_prefix = sock.recv(4)
            if not length_prefix:
                print("Connection closed or no data received.")
                continue
            # Unpack the length prefix to get the message size
            data_length = struct.unpack('!I', length_prefix)[0]

            # Receive the entire message based on the length
            received_data = b""
            while len(received_data) < data_length:
                chunk = sock.recv(1024)  # Read in chunks
                if not chunk:
                    break
                received_data += chunk
            #data = socket.recv(64000)

            message = loads(received_data)
            self.addMessageList(message)


    def run(self):
        self.activeListening()

    def stop(self):
        self._stop_event.set()




