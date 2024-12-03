from collections.abc import Callable
from threading import Thread
from typing import Any, Iterable, List, Mapping, Union
from MessageClasses import RequestMessage


class AcceptedRequestQueue(Thread):
    """Queue that stores requests that has been accepted

    Args:
        None:
    
    """
    __acceptedRequests:List[List[Union[RequestMessage, int]]]
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
        self.__acceptedRequests = []

    def run(self) -> None:
        while True:
            self.decrementTime()
    
    def isEmpty(self) -> bool:
        """Method for checking if there are any accepted requests

        Args:
            None

        Returns:
            isEmpty (bool): True if the list is empty
        
        """
        if len(self.__acceptedRequests) == 0:
            return True
        else:
            return False
    
    def getIDInQueue(self) -> List[int]:
        """Method for getting a list of taskID accepted

        Args:
            None:
        
        Returns:
            idInQueue (List[int]): List containing ID in list
        
        """
        IDList: List[int] = []
        for message in self.__acceptedRequests:
            IDList.append(message[0].getTaskID())
        return IDList

    
    def addMessage(self, message:RequestMessage, time) -> None:
        """Method for adding request to list

        Args:
            message (RequestMessage): The request message that has to be added
        
        Returns:
            None:
        
        """
        self.__acceptedRequests.append([message, self.__TIME_TO_LIVE])
    
    def removeMessage(self, taskID:int) -> None:
        """Method for removing request with ID

        Args:
            taskID (int): The id of the request that has to be removed

        Returns:
            None:
        
        """
        for message in self.__acceptedRequests:
            if message[0].get_task_id() == taskID:
                self.__acceptedRequests.remove(message)
    
    def decrementTime(self) -> None:
        """Method for decreasing the time to live

        Args:
            None:
        
        Returns:
            None:
        
        """
        if not self.isEmpty():
            for message in self.__acceptedRequests:
                if message[1] == 0:
                    self.__acceptedRequests.remove(message)
                else:
                    message[1] -= 1
    
    def getLength(self) -> int:
        """Method for getting amount of accepted requests

        Args:
            None:

        Returns:
            length (int): Returns length of list with accepted request
        
        """
        return len(self.__acceptedRequests)
    
    