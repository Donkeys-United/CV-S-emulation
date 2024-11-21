#Libraries
import threading
from Task import Task
from MessageClasses import *
#from CommunicationThread import * #Fiks navn af fil senere


class TaskHandlerThread(threading.Thread):

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
        Sends a request message for a task to the CommunicationThread.
        """
        # Create a RequestMessage object
        sendRequestMessage = RequestMessage(
            unix_time_limit=task.getUnixTimestampLimit(),
            task_id=str(task.getTaskId())  # Ensure task ID is a string as expected by RequestMessage
        )

        # Add the message to the CommunicationThread
        CommunicationThread().addMessage(sendRequestMessage)

        # Debug output
        print(f"Sending: {sendRequestMessage}")

        # Return for verification
        return sendRequestMessage.getTaskID(), sendRequestMessage.getUnixTimeLimit()
            

    def sendRespond(self, task):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        sendRequestMessage = RequestMessage(
            taskID=task.getTaskId(),
            unixTimeLimit=task.getUnixTimestampLimit()
        )

        # Add the message to the CommunicationThread
        CommunicationThread().addMessage(sendRequestMessage)

        # Print and return
        print(f"Sending: {sendRequestMessage}")
        return sendRequestMessage.getTaskID(), sendRequestMessage.getUnixTimeLimit()



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
        



class CommunicationThread():

    def __init__(self):
        self.tasklist = []


    def addMessage(self, task: Task):
        self.tasklist.append(task)


# Create instances
task = Task(timeLimit=3600)  # Create a Task with a 1-hour limit
thread = TaskHandlerThread(name="TaskHandler", delay=1)

# Start the thread (if needed)
thread.start()

# Send a task request
taskID, timeLimit = thread.sendRequest(task)  # Call on the instance
print(f"TaskID: {taskID}, TimeLimit: {timeLimit}")


