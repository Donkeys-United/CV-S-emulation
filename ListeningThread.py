import threading
from CommunicationThread import CommunicationThread
from MessageClasses import Message
import socket
from pickle import loads

class ListeningThread(threading.Thread):

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
        self.communicationThread.messageList.append(message)
    
    def activeListening(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        connection.bind((self.IP_ADDR, self.port))
        while not self._stop_event.is_set():
            connection.listen()
            incoming_message = connection.accept()
            unpickled_message = loads(incoming_message)
            self.addMessageList(unpickled_message)

    def run(self):
        self.activeListening()

    def stop(self):
        self._stop_event.set()




