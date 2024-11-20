#Libraries
import threading
from Task import Task


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
        

    def sendRequest(self,):
        """
        Method to send a request to other satellites in order to find out if they are able to perform the task
        """
        pass
            

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
        pass

thread = TaskHandlerThread(name = "mainWorker", delay = 2)
thread.start()



