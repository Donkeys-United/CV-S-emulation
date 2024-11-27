from collections.abc import Callable
from Task import Task
from threading import Thread
from MessageClasses import RequestMessage, RespondMessage, ImageDataMessage, ResponseNackMessage, ProcessedDataMessage
from AcceptedRequestQueue import AcceptedRequestQueue
from typing import Any, Iterable, List, Mapping
from TransmissionThread import TransmissionThread
from ListeningThread import ListeningThread
import json
from TaskHandlerThread import TaskHandlerThread

class CommunicationThread(Thread):
    LISTENING_PORTS_LEFT: int = 4500
    LISTENING_PORTS_RIGHT: int = 4600
    transmissionQueue:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    messageList:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    responseList: List[RespondMessage] = []
    acceptedRequestsQueue:AcceptedRequestQueue = AcceptedRequestQueue()
    transmissionThread:TransmissionThread
    listeningThreadLeft: ListeningThread
    listeningThreadRight: ListeningThread
    config: dict
    taskHandlerThread: TaskHandlerThread
    taskWaitingList: List[Task] = []

    def __init__(
            self,
            satelliteID: int,
            config: dict,
            taskHandlerThread: TaskHandlerThread,
            group: None = None, target: Callable[..., object] | None = None, name: str | None = None,
            args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
            ) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

        #Get config dictionary
        self.config = config

        #Setup and start transmissionThread using config
        try:
            for satellites in self.config['satellites']:
                if satellites['id'] == satelliteID:
                    connections = satellites['connections']
                    break
            connectionsIP = []
            for satellites in self.config['satellites']:
                if satellites['id'] in connections:
                    connectionsIP.append(satellites['ip_address'])
        except:
            raise ValueError('Config file is not correct')
        self.acceptedRequestsQueue.start()
        self.transmissionThread = TransmissionThread(
            satelliteID=satelliteID,
            neighbourSatelliteIDs=connections,
            neighbourSatelliteAddrs=connectionsIP,
            groundstationAddr=config['ground_station_ip']
            )
        self.transmissionThread.start()
        
        #Initiate listeningThreads
        self.listeningThreadLeft = ListeningThread(port=self.LISTENING_PORTS_LEFT, communicationThread=self)
        self.listeningThreadRight = ListeningThread(port=self.LISTENING_PORTS_RIGHT, communicationThread=self)
        self.listeningThreadLeft.start()
        self.listeningThreadRight.start()

        #Create reference to TaskHandlerThread
        self.taskHandlerThread = taskHandlerThread
            


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
                self.addTransmission(message=message)
        elif type(message) == RespondMessage:
            messageID = message.getTaskID()
            for task in self.taskWaitingList:
                if task.getTaskID() == messageID:
                    self.responseList.append(message)
                    break
                elif task == self.taskWaitingList[-1]:
                    self.addTransmission(message=message)
        elif type(message) == ImageDataMessage:
            messagePayload = message.getPayload()
            if messagePayload.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                self.taskHandlerThread.appendTask(messagePayload)
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
    
    def giveTask(self, task: Task) -> None:
        self.taskWaitingList.append(task)