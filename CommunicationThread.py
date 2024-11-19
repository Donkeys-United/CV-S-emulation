from threading import Thread
from MessageClasses import Message
from typing import List

class CommunicationThread(Thread):
    unAcceptedRequests:List[Message] = []
    transmissionQueue:List[Message] = []
    messageList:List[Message] = []

    def run(self) -> None:
        return super().run()
    
    