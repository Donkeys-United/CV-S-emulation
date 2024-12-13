from collections.abc import Callable
from Task import Task
from threading import Thread
from MessageClasses import RequestMessage, RespondMessage, ImageDataMessage, ResponseNackMessage, ProcessedDataMessage, Message
from AcceptedRequestQueue import AcceptedRequestQueue
from typing import Any, Iterable, List, Mapping, TYPE_CHECKING
import time
from responseHandler import ResponseHandler
import logging

if TYPE_CHECKING:
    from TaskHandlerThread import TaskHandlerThread
    from OrbitalPositionThread import OrbitalPositionThread

# Configure logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()     # Also log to the console
    ]
)

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
    transmissionQueue:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    messageList:List[RequestMessage | RespondMessage | ImageDataMessage | ResponseNackMessage | ProcessedDataMessage] = []
    responseList: List[RespondMessage] = []
    config: dict
    acceptedRequestsQueue:AcceptedRequestQueue = AcceptedRequestQueue()
    responseHandler: ResponseHandler

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
        self.satelliteID = satelliteID

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
                if satellites['id'] == connections[0]:
                    connectionsIP.append(satellites['ip_address'])
            for satellites in self.config['satellites']:
                if satellites['id'] == connections[1]:
                    connectionsIP.append(satellites['ip_address'])
        except:
            raise ValueError('Config file is not correct')
        
        self.connectionsIP = connectionsIP
        self.connections = connections
        self.transmissionThread: TransmissionThread = TransmissionThread(
            communicationThread=self,
            neighbourSatelliteIDs=connections,
            neighbourSatelliteAddrs=connectionsIP,
            groundstationAddr=(config['ground_station_ip'],config['ground_station_port'])
            )
        self.transmissionThread.start()
        

        #Initiate listeningThreads
        from ListeningThread import ListeningThread
        self.responseHandler = ResponseHandler(self, self.orbitalPositionThread)
        self.listeningThreadLeft: ListeningThread = ListeningThread(port=self.LISTENING_PORTS_LEFT, communicationThread=self)
        self.listeningThreadRight: ListeningThread = ListeningThread(port=self.LISTENING_PORTS_RIGHT, communicationThread=self)
        self.listeningThreadLeft.start()
        self.listeningThreadRight.start()
        self.responseHandler.start()

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
            task_source = message.getTaskID() & 0x0000FFFFFFFFFFFF
            time_limit  = message.getUnixTimestampLimit()

            allocation = self.taskHandlerThread.allocateTaskToSelf(time_limit, task_source)
            if allocation[0]: #add input - ONLY TIMELIMIT
                freq = allocation[1]
                self.acceptedRequestsQueue.addMessage(message=message, frequency=freq)
                time_limit_left = message.getUnixTimestampLimit() - time.time()
                logging.info("Accepted Request from satellite %s - Info: \n\tTaskID: %s \n\tTask Source: %s \n\tRemaining Time In Time Limit: %s", message.lastSenderID, message.getTaskID(), task_source, time_limit_left)
                self.sendRespond(message=message)
            else:
                time_limit_left = message.getUnixTimestampLimit() - time.time()
                logging.info("Denied Request from satellite %s - Info: \n\tTaskID: %s \n\tTask Source: %s \n\tRemaining Time In Time Limit: %s", message.lastSenderID, message.getTaskID(), task_source, time_limit_left)
                self.addTransmission(message=message)

        elif type(message) == RespondMessage:
            self.responseHandler.addResponse(message)

        elif type(message) == ImageDataMessage:
            messagePayload = message.getPayload()
            if messagePayload.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                payload = message.getPayload()
                task_source = payload.getSource()
                taskID = messagePayload.getTaskID()
                frequency = self.acceptedRequestsQueue.getFrequency(taskID=taskID)
                logging.info("ImageData for Accepted Request Received - Info: \n\tTaskID: %s \n\tTask Source: %s \n\tRemaining Time In Time Limit: %s", message.lastSenderID, message.getTaskID(), task_source, time_limit_left)
                self.taskHandlerThread.appendTask(messagePayload, frequency=frequency)
                self.acceptedRequestsQueue.removeMessage(taskID=taskID)
            else:
                #print(f'forwarded task with ID {int.from_bytes(message.getTaskID(),"big")}')
                self.addTransmission(message=message)

        elif type(message) == ResponseNackMessage:
            if message.getTaskID() in self.acceptedRequestsQueue.getIDInQueue():
                print(f'removed accepted request with ID {message.getTaskID()}')
                self.acceptedRequestsQueue.removeMessage(message.getTaskID())
            else:
                print('forward ResponseNackMessage')
                self.addTransmission(message=message)
                
        elif type(message) == ProcessedDataMessage:
            print('forwards processed data')
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
        print(f'added task with ID {int.from_bytes(task.getTaskID(), "big")}')
        self.responseHandler.addTask(task=task)
    
    def sendRespond(self,  message: RequestMessage):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        sendRespondMessage = RespondMessage(
            taskID=message.getTaskID(),
            source=self.satelliteID,#message.getTaskID() & 0x0000FFFFFFFFFFFF,
            firstHopID = message.lastSenderID
        )

        self.addTransmission(sendRespondMessage)
 

        # Print and return
        print(f"Sending: {sendRespondMessage}")
        return sendRespondMessage.getTaskID(), sendRespondMessage.getTaskID()
