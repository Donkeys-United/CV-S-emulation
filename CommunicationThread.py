from collections.abc import Callable
from Task import Task
from threading import Thread
from MessageClasses import RequestMessage, RespondMessage, ImageDataMessage, ResponseNackMessage, ProcessedDataMessage, Message
from AcceptedRequestQueue import AcceptedRequestQueue
from typing import Any, Iterable, List, Mapping, TYPE_CHECKING
import time

if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from OrbitalPositionThread import OrbitalPositionThread

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

    def __init__(
            self,
            satelliteID: int,
            config: dict,
            taskHandlerThread,
            orbitalPositionThread,
            group: None = None, target: Callable[..., object] | None = None, name: str | None = None,
            args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
            ) -> None:
        from TransmissionThread import TransmissionThread
        from ListeningThread import ListeningThread
        from TaskHandlerThread import TaskHandlerThread
        from OrbitalPositionThread import OrbitalPositionThread

        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.orbitalPositionThread = orbitalPositionThread
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
        
        print(connections, connectionsIP)

        self.transmissionThread: TransmissionThread = TransmissionThread(
            communicationThread=self,
            neighbourSatelliteIDs=connections,
            neighbourSatelliteAddrs=connectionsIP,
            groundstationAddr=config['ground_station_ip']
            )
        self.transmissionThread.start()
        

        #Initiate listeningThreads
        from ListeningThread import ListeningThread
        self.listeningThreadLeft: ListeningThread = ListeningThread(port=self.LISTENING_PORTS_LEFT, communicationThread=self)
        self.listeningThreadRight: ListeningThread = ListeningThread(port=self.LISTENING_PORTS_RIGHT, communicationThread=self)
        self.listeningThreadLeft.start()
        self.listeningThreadRight.start()

        #Create reference to TaskHandlerThread
        self.taskHandlerThread: TaskHandlerThread = taskHandlerThread
            


    def run(self) -> None:
        while True:
            while len(self.messageList) != 0:
                for message in self.messageList:
                    self.messageTypeHandle(message=message)
                    self.messageList.remove(message)
            time.sleep(2)

    
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
                self.sendRespond(message=message)
            else:
                self.addTransmission(message=message)

        elif type(message) == RespondMessage:
            messageID = message.getTaskID()
            for task in self.taskWaitingList:
                messageID2 = task.getTaskID()
                if messageID2 == messageID:
                    for response in self.responseList:
                        if response.getTaskID() == messageID:
                            priorityList = self.orbitalPositionThread.getSatellitePriorityList()
                            source1 = int.from_bytes(messageID[0:6], byteorder='big')
                            source2 = int.from_bytes(messageID2[0:6], byteorder='big')
                            for priority in priorityList:
                                if priority == source1 or priority == source2:
                                    selected_source = source1 if priority == source1 else source2
                                    dataPacket = ImageDataMessage(payload=task, firstHopID=selected_source)
                                    self.transmissionQueue.append(dataPacket)
                                    break
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
            self.transmissionQueue.append(message)
    

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
    
    def sendRespond(self,  message: RequestMessage):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        sendRespondMessage = RespondMessage(
            taskID=message.getTaskID(),
            source=message.getTaskID() & 0x0000FFFFFFFFFFFF,
            firstHopID = message.lastSenderID
        )

        self.communicationThread.addTransmission(sendRespondMessage)
 

        # Print and return
        print(f"Sending: {sendRespondMessage}")
        return sendRespondMessage.getTaskID(), sendRespondMessage.getTaskID()
