from collections.abc import Callable
from Task import Task
from threading import Thread
from MessageClasses import RequestMessage, RespondMessage, ImageDataMessage, ResponseNackMessage, ProcessedDataMessage
from AcceptedRequestQueue import AcceptedRequestQueue
from typing import Any, Iterable, List, Mapping
from TransmissionThread import TransmissionThread

class CommunicationThread(Thread):
    unAcceptedRequests:List[RequestMessage] = []
    transmissionQueue:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    messageList:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    acceptedRequestsQueue:AcceptedRequestQueue
    transmission:TransmissionThread

    def __init__(
            self,
            group: None = None, target: Callable[..., object] | None = None, name: str | None = None,
            args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
            ) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.acceptedRequestsQueue = AcceptedRequestQueue()
        self.acceptedRequestsQueue.start()
        self.transmission = TransmissionThread()


    def run(self) -> None:
        return super().run()
    
    def messageTypeHandle(
            self,
            message: RequestMessage | ImageDataMessage | RespondMessage | ResponseNackMessage | ProcessedDataMessage
            ) -> None:
        
        if type(message) == RequestMessage:
            pass #Insert allocation function
        elif type(message) == RespondMessage:
            pass
        elif type(message) == ImageDataMessage:
            if message.getPayload() in self.acceptedRequestsQueue:
                messagePayload = message.getPayload()
                requestedTask = Task(messagePayload.getUnixTimestampLimit())
                requestedTask.appendImage(messagePayload.getFileName(), messagePayload.getImage(), messagePayload.getLocation())
                #Insert TaskHandlerThread add to allocatedTasks
            else:
                pass
        elif type(message) == ResponseNackMessage:
            if message.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                self.acceptedRequestsQueue.removeMessage(message.getTaskID())
            else:
                pass
        elif type(message) == ProcessedDataMessage:
            pass
    
    def priorityCheck(sourceMac:int) -> int:
        pass #I need constellation to do this