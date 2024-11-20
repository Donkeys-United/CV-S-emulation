#Libraries
import threading
from Task import Task
from MessageClasses import *
from communicationthread import * #Fiks navn af fil senere


class TaskHandlerThread(threading.Thread):

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
        

    def sendRequest(self, task: Task, communication_thread):
        """
        Method to send a request to the CommunicationThread, which forwards it to other satellites.
        
        Parameters:
        - task: Task object containing task details.
        - communication_thread: An instance of the CommunicationThread to send the message.
        
        Returns:
        - taskID: int
        - timeLimit: float
        """
        sendRequestMessage = RequestMessage(
            taskID = task.taskID,
            unixTimeLimit = task.unixTimeLimit
        )

        # Use the RequestMessage methods to get the task details
        taskID = sendRequestMessage.getTaskID()
        timeLimit = sendRequestMessage.getUnixTimeLimit()

        communication_thread.addMessage(sendRequestMessage)

        #Print for debugging
        print(sendRequestMessage)
        return taskID, timeLimit #Nødvendigt at retunere?
            

    def sendRespond(self,):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        pass

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



