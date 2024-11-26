from collections.abc import Callable
from threading import Thread
from typing import Any, Iterable, List, Mapping
from MessageClasses import RequestMessage


class AcceptedRequestQueue(Thread):
    __acceptedRequests:List[List[RequestMessage, int]]
    __TIME_TO_LIVE:int = 3600

    def __init__(
            self,
            group: None = None,
            target: Callable[..., object] | None = None, name: str | None = None,
            args: Iterable[Any] = ...,
            kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
            ) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def run(self) -> None:
        while True:
            self.decrementTime()
    
    def isEmpty(self) -> bool:
        if len(self.__acceptedRequests) == 0:
            return True
        else:
            return False
    
    def getIDInQueue(self) -> List[int]:
        IDList: List[int] = []
        for message in self.__acceptedRequests:
            IDList.append(message[0].getTaskID())
        return IDList

    
    def addMessage(self, message:RequestMessage, time) -> None:
        self.__acceptedRequests.append([message, self.__TIME_TO_LIVE])
    
    def removeMessage(self, taskID:int) -> None:
        for message in self.__acceptedRequests:
            if message[0].get_task_id() == taskID:
                self.__acceptedRequests.remove(message)
    
    def decrementTime(self) -> None:
        if not self.isEmpty():
            for message in self.__acceptedRequests:
                if message[1] == 0:
                    self.__acceptedRequests.remove(message)
                else:
                    message[1] -= 1
    
    def getLength(self) -> int:
        return len(self.__acceptedRequests)
    
    