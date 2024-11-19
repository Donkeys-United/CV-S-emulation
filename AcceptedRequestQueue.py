from threading import Thread
from typing import List
from MessageClasses import RequestMessage


class AcceptedRequestQueue(Thread):
    __acceptedRequests:List[List[RequestMessage, int]]
    __TIME_TO_LIVE:int = 3600

    def run(self) -> None:
        return super().run()
    
    def isEmpty(self) -> bool:
        if len(self.__acceptedRequests) == 0:
            return True
        else:
            return False
    
    def addMessage(self, message:RequestMessage, time) -> None:
        self.__acceptedRequests.append([message, self.__TIME_TO_LIVE])
    
    def removeMessage(self, taskID:int) -> None:
        self.__acceptedRequests.remove(RequestMessage.get_task_id(taskID))
    
    def decrementTime(self) -> None:
        if not self.isEmpty():
            for message in self.__acceptedRequests:
                if message[1] == 0:
                    self.__acceptedRequests.remove(message)
                else:
                    message[1] -= 1
    
    