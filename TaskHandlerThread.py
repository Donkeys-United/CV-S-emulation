#Libraries
import threading
from Task import Task
from OribtalPositionThread import canExecuteMission


class TaskHandlerThread(threading.Thread):

    #Attributes:

    def __init__(self, name, delay):
        super().__init__()
        self.name = name
        self.delay = delay
        self.running = True
        self.__allocatedTasks = []
        self.__allocatedTasks = []

    def run(self,):
        while self.running:
            pass


    def doAllocateTaskToSelf(self, task: Task,__unallocatedTasks, __allocatedTasks):
        """
        Method used to either allocate a task to a satellite itself, or send a request message to another satellite
        """
        if __unallocatedTasks != None:
            x = OribtalPositionThread.canExecuteMission() #er lidt i tvivl om syntaxen er rigtig, men ellers fiks senere
            if x == True:
                __allocatedTasks.append[task]
            else:
                TaskHandlerThread.sendRequest(Task)
        else:
            pass
        

    def sendRequest(self,):
        pass
            

    def sendRespond(self,):
        pass

    def sendDataPacket(self,):
        pass

    def changeFrequency(self, frequency: int):
        pass

    def getAcceptedTaskTotal(self, ):
        pass

    def enqueueUnallocatedTask(self, task: Task):
        pass

thread = TaskHandlerThread(name="mainWorker", delay=2)
thread.start()



