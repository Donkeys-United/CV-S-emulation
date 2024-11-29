from collections.abc import Callable
from Task import Task
from threading import Thread
from MessageClasses import RequestMessage, RespondMessage, ImageDataMessage, ResponseNackMessage, ProcessedDataMessage
from AcceptedRequestQueue import AcceptedRequestQueue
from typing import Any, Iterable, List, Mapping, TYPE_CHECKING

if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from TransmissionThread import TransmissionThread
    from ListeningThread import ListeningThread

class CommunicationThread(Thread):
    """The CommunicationThread that handles incoming and outgoing messages

    Args:
        satelliteID (int): The local satellite ID
        config (dict): The config json file loaded to a dictionary
        taskHandlerThread (TaskHandlerThread): A reference to the local TaskHandlerThread
    """

    #Constants
    LISTENING_PORTS_LEFT: int = 4500
    LISTENING_PORTS_RIGHT: int = 4600

    #Variables
    taskWaitingList: List[Task] = []
    transmissionQueue:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    messageList:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    responseList: List[RespondMessage] = []
    config: dict
    acceptedRequestsQueue:AcceptedRequestQueue = AcceptedRequestQueue()

    #Threads
    listeningThreadLeft: ListeningThread
    listeningThreadRight: ListeningThread
    taskHandlerThread: TaskHandlerThread

    def __init__(
            self,
            satelliteID: int,
            config: dict,
            taskHandlerThread,
            group: None = None, target: Callable[..., object] | None = None, name: str | None = None,
            args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
            ) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

        self.taskHandlerThread = taskHandlerThread
        self.acceptedRequestsQueue = AcceptedRequestQueue()
        self.acceptedRequestsQueue.start()

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
        """Method for handling incoming messages

        Args:
            message (Message): Incoming message

        Returns:
            None:
        
        """
        
        if type(message) == RequestMessage:
            if self.taskHandlerThread.allocateTaskToSelf(): #add input - ONLY TIMELIMIT
                self.acceptedRequestsQueue.addMessage(message=message)
            else:
                self.addTransmission(message=message)

        elif type(message) == RespondMessage:
            messageID = message.getTaskID()
            for task in self.taskWaitingList:
                if task.getTaskID() == messageID:
                    for response in self.responseList:
                        if response.getTaskID() == messageID:
                            
                            break
                        else:
                            self.responseList.append(message)
                    break
                elif task == self.taskWaitingList[-1]:
                    self.addTransmission(message=message)

        elif type(message) == ImageDataMessage:
            messagePayload = message.getPayload()
            if messagePayload.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                self.taskHandlerThread.appendTask(messagePayload)
            else:
                self.addTransmission(message=message)

        elif type(message) == ResponseNackMessage:
            if message.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                self.acceptedRequestsQueue.removeMessage(message.getTaskID())
            else:
                self.addTransmission(message=message)
                
        elif type(message) == ProcessedDataMessage:
            pass
    
    def priorityCheck(sourceMac:int) -> int:
        pass #I need constellation to do this

    def addTransmission(
            self,
            message: RequestMessage | ImageDataMessage | RespondMessage | ResponseNackMessage | ProcessedDataMessage
            ) -> None:
        """Method for adding a transmission that has to be sent by the transmissionThread

        Args:
            message (Message): Message that has to be sent

        Returns:
            None:
        
        """
        self.transmissionQueue.append(message)
    
    def getTotalAcceptedTasks(self) -> int:
        """Method for getting the total amount of remote tasks accepted by the taskHandlerThread

        Args:
            None:
        
        Returns:
            amount (int): Amount of tasks in acceptedTaskQueue
        
        """
        return self.acceptedRequestsQueue.getLength()
    
    def giveTask(self, task: Task) -> None:
        self.taskWaitingList.append(task)