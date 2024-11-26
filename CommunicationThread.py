from collections.abc import Callable
from Task import Task
from threading import Thread
from MessageClasses import RequestMessage, RespondMessage, ImageDataMessage, ResponseNackMessage, ProcessedDataMessage
from AcceptedRequestQueue import AcceptedRequestQueue
from typing import Any, Iterable, List, Mapping
from TransmissionThread import TransmissionThread
import json
from TaskHandlerThread import TaskHandlerThread

class CommunicationThread(Thread):
    transmissionQueue:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    messageList:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    acceptedRequestsQueue:AcceptedRequestQueue
    transmission:TransmissionThread
    config: json
    taskHandlerThread: TaskHandlerThread

    def __init__(
            self,
            satelliteID: int,
            config: json,
            taskHandlerThread: TaskHandlerThread,
            group: None = None, target: Callable[..., object] | None = None, name: str | None = None,
            args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
            ) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.config = config
        self.acceptedRequestsQueue = AcceptedRequestQueue()
        self.acceptedRequestsQueue.start()
        self.transmission = TransmissionThread()
        self.taskHandlerThread = taskHandlerThread
        with open(config, 'r') as f:
            config_data = json.load(f)
            


    def run(self) -> None:
        return super().run()
    
    def messageTypeHandle(
            self,
            message: RequestMessage | ImageDataMessage | RespondMessage | ResponseNackMessage | ProcessedDataMessage
            ) -> None:
        
        if type(message) == RequestMessage:
            if self.taskHandlerThread.allocateTaskToSelf(): #add input - ONLY TIMELIMIT
                self.acceptedRequestsQueue.addMessage(message=message)
            else:
                pass #add send transmission
        elif type(message) == RespondMessage:
            pass
        elif type(message) == ImageDataMessage:
            messagePayload = message.getPayload()
            if messagePayload.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                requestedTask = Task(messagePayload.getUnixTimestampLimit())
                requestedTask.appendImage(messagePayload.getFileName(), messagePayload.getImage(), messagePayload.getLocation())
                self.taskHandlerThread.appendTask(requestedTask) # payload er allerede Task Object Instance - Nicolai Fiks.
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

    def addTransmission(
            self,
            message: RequestMessage | ImageDataMessage | RespondMessage | ResponseNackMessage | ProcessedDataMessage
            ) -> None:
        self.transmissionQueue.append(message)
    
    def getTotalAcceptedTasks(self) -> int:
        return self.acceptedRequestsQueue.getLength()