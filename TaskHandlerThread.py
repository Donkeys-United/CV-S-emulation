#Libraries
import threading
from Task import Task
from OribtalPositionThread import canExecuteMission


class TaskHandlerThread(threading.Thread):

    #Attributes:
    __allocatedTasks = []
    __unallocatedTasks = []

    def __init__(self, name, delay):
        super().__init__()
        self.name = name
        self.delay = delay
        self.running = True

    def run(self,):
        while self.running:
            pass


    def doAllocateTaskToSelf(self, task: Task):
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



