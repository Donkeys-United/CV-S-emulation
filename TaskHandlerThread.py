#Libraries
import threading
from Task import Task
from MessageClasses import *
from CommunicationThread import * 


class TaskHandlerThread(threading.Thread):

    def __init__(self, name, delay):
        super().__init__()
        self.name = name
        self.delay = delay
        self.running = True
        self.__allocatedTasks = []
        self.__unallocatedTasks = []
        


    def run(self, thread, CommThread):
        """
        Method to initiate the different threads in the system(Main loop maybe?)
        """
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
        Sends a request message for a task to the CommunicationThread.
        """
        # Create a RequestMessage object
        sendRequestMessage = RequestMessage(
            unixTimeLimit=task.getUnixTimestampLimit(),
            taskID=task.getTaskID()
        )

        # Print the message object directly
        print(f"Sending message: {sendRequestMessage}")

        # Add the message to the CommunicationThread
        #thread2.addMessage(sendRequestMessage)

        # Return the task ID and time limit
        return sendRequestMessage.getTaskID(), sendRequestMessage.getUnixTimeLimit()


    def sendRespond(self, task: Task):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        sendRespondMessage = RespondMessage(
            taskID=task.getTaskID(),
            source=task.getTaskID()
        )

        # Add the message to the CommunicationThread
        #thread2.addMessage(sendRespondMessage)
 

        # Print and return
        print(f"Sending: {sendRespondMessage}")
        return sendRespondMessage.getTaskID(), sendRespondMessage.getTaskID()



    def sendDataPacket(self, task: Task):
        """
        Send task packet to 
        """
        sendDataMessage = ImageDataMessage(
            image = task.getImage(),
            taskID = task.getTaskID(),
            fileName = task.getFileName(),
            location = task.getLocation(),
            unixTimestamp = task.getUnixTimestamp(),
            unixTimeLimit = task.getUnixTimestampLimit()
            )

        CommThread.addMessage(sendDataMessage)
        return sendDataMessage

    """
    def changeFrequency(self, frequency: int):
        pass
    """

    def getAcceptedTaskTotal(self, __allocatedTasks: list):
        """
        Method to get the ammount of accepted tasks a satellite has
        """
        return len(__allocatedTasks)


    def enqueueUnallocatedTask(self, task: Task):
        self.__unallocatedTasks.append(task)
        

#Test for the different messages
thread = TaskHandlerThread(name="TaskHandler", delay = 1)
CommThread = CommunicationThread(name="CommThread", delay = 1)

thread.start()
CommThread.start() 

"""
# Create instances
task = Task(timeLimit=3600)  # Create a Task with a 1-hour limit

# Send a task request
taskID, timeLimit = thread.sendRequest(task)  # Call on the instance
print(f"TaskID: {taskID}, TimeLimit: {timeLimit}")

#send a task respond
taskID, source= thread.sendRespond(task)  # Call on the instance
"""