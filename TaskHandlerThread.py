#Libraries
import threading
from Task import Task
from MessageClasses import *
from CommunicationThread import * #Fiks navn af fil senere


class TaskHandlerThread(threading.Thread, CommunicationThread):

    #Attributes:

    def __init__(self, name, delay):
        super().__init__()
        self.name = name
        self.delay = delay
        self.running = True
        self.__allocatedTasks = []
        self.__unallocatedTasks = []



    def run(self,):
        while self.running:
            pass


    def allocateTaskToSelf(self, task: Task, __unallocatedTasks: list, __allocatedTasks: list):
        """
        Method used to either allocate a task to a satellite itself, or send a request message to another satellite
        """
        if __unallocatedTasks != None:
            task = __unallocatedTasks[0]
            x = "Insert Kristian Meth"
            if x == True:
                self.__allocatedTasks.append[task]
            else:
                TaskHandlerThread.sendRequest(Task)
        else:
            pass
        

    def sendRequest(self, task: Task):
        """
        Method to send a request to the CommunicationThread, which forwards it to other satellites.
        
        Parameters:
        - task: Task object containing task details.
        - communication_thread: An instance of the CommunicationThread to send the message.
        
        Returns:
        - taskID: int
        - timeLimit: float
        """
        #Creates an object of the RequestMessage
        sendRequestMessage = RequestMessage(
            taskID = task.taskID,
            unixTimeLimit = task.unixTimestamp
        )

        # Use the RequestMessage methods to get the task details
        taskID = sendRequestMessage.getTaskID()
        timeLimit = sendRequestMessage.getUnixTimeLimit()

        CommunicationThread.addMessage(sendRequestMessage)

        #Print for debugging
        print(sendRequestMessage)
        return taskID, timeLimit #Nødvendigt at retunere?
            

    def sendRespond(self, task):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        
        #Creates an object of the RespondMessage
        sendRespondMessage = RespondMessage(
            taskID = task.taskID,
            source = task.source
        )

        taskID = sendRespondMessage.getTaskID()
        source = sendRespondMessage.getSource()

        CommunicationThread.addMessage(sendRespondMessage)

        #Print for debugging
        print(sendRespondMessage)
        return taskID, timeLimit #Nødvendigt at retunere?


    def sendDataPacket(self,):
        """
        Send task packet to 
        """
        pass


    def changeFrequency(self, frequency: int):
        """
        Method to adjust the GPU frequency - maybe declared in another class, not this one. TBD
        """
        pass


    def getAcceptedTaskTotal(self, ):
        """
        Method to get the ammount of accepted tasks a satellite has
        """
        pass


    def enqueueUnallocatedTask(self, task: Task):
        self.__unallocatedTasks.append(task)
        

thread = TaskHandlerThread(name = "mainWorker", delay = 2)
thread.start()



