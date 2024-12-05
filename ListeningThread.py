import threading
from MessageClasses import Message
import socket
from pickle import loads

class ListeningThread(threading.Thread):
    """Class for Listening Thread. Used for listening on a specific port for incoming messages.
    """
    from CommunicationThread import CommunicationThread
    HOSTNAME = socket.gethostname()
    IP_ADDR = socket.gethostbyname(HOSTNAME)

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

        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection.bind((self.IP_ADDR, self.port))
        while not self._stop_event.is_set():
            incoming_message, addr = connection.recvfrom(1024)
            unpickled_message = loads(incoming_message)
            self.addMessageList(unpickled_message)

    def run(self):
        self.activeListening()

    def stop(self):
        self._stop_event.set()




