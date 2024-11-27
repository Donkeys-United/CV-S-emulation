#Libraries
import random, threading, time
from Task import Task
from MessageClasses import *
#from MissionThread import *
from CommunicationThread import CommunicationThread
from PriorityQueue import PriorityQueue

class TaskHandlerThread(threading.Thread):

    def __init__(self, communicationThread: CommunicationThread):
        super().__init__()
        self.running = True
        self.__allocatedTasks = PriorityQueue()
        self.__unallocatedTasks = PriorityQueue()
        self.communicationThread = communicationThread


    def run(self):
        """
        Method to initiate the different threads in the system(Main loop maybe?)
        """
        while self.running:
            if self.__unallocatedTasks != None:
                allocateToSelf = self.allocateTaskToSelf(self.__unallocatedTasks.nextTask())
                if allocateToSelf == True:
                    self.__allocatedTasks.addTaskToQueue(self.__unallocatedTasks.nextTask())
                else:
                    self.sendRequest(self.__unallocatedTasks.nextTask())
                    self.communicationThread.giveTask(self.__unallocatedTasks.nextTask())
            else:
                time.sleep(1)




    # Det her skal lige fikses, så det kører fra run().
    # mucho fix
    def allocateTaskToSelf(self, task: Task):
        """
        Method used to either allocate a task to a satellite itself, or send a request message to another satellite
        """
        trueFalseMethod = random.choice([True, False])
        if trueFalseMethod == True:
            return True
        else: 
            return False
        

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
        #print(f"Sending message: {sendRequestMessage}")

        # Add the message to the CommunicationThread
        self.communicationThread.addTransmission(sendRequestMessage)

        # Return the task ID and time limit
        #return sendRequestMessage.getTaskID(), sendRequestMessage.getUnixTimeLimit()


    def sendRespond(self, task: Task, message: Message):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        sendRespondMessage = RespondMessage(
            taskID=task.getTaskID(),
            source=task.getSource(),
            firstHopID = message.lastSenderID
        )

        self.communicationThread.addTransmission(sendRespondMessage)
 

        # Print and return
        print(f"Sending: {sendRespondMessage}")
        return sendRespondMessage.getTaskID(), sendRespondMessage.getTaskID()



    def sendDataPacket(self, task: Task, message: Message):
        """
        Send task packet to 
        """
        sendDataMessage = ImageDataMessage(payload=task, firstHopID=message.lastSenderID)

        self.communicationThread.addTransmission(sendDataMessage)
        return sendDataMessage


    def getAcceptedTaskTotal(self):
        """
        Method to get the ammount of accepted tasks a satellite has
        """
        return len(self.__allocatedTasks) + self.communicationThread.getTotalAcceptedTasks()


    def appendTask(self, task: Task):
        self.__allocatedTasks.addTaskToQueue(task)
    
    def appendUnallocatedTask(self, task: Task):
        self.__unallocatedTasks.addTaskToQueue(task)


#####################################################################################################
class CommunicationThread(threading.Thread):

    def __init__(self):
        super().__init__()

        self.tasklist = []

    def addTransmission(self, message: Message):
        self.tasklist.append(message)
        print(f"The tasklist is now: {[str(msg) for msg in self.tasklist]}")

    def getTotalAcceptedTasks(self):
        return 0

#Test for the different messages
thread = TaskHandlerThread()
CommThread = CommunicationThread()

thread.start()
CommThread.start() 

"""
Generate a random task
"""
# Generate a random 48-bit integer for satelliteID
satelliteID = random.randint(0, 2**48 - 1)
# Generate a random 8-bit integer for incrementingID (or use a counter if needed)
incrementingID = random.randint(0, 255)

# Construct self.taskID
taskIDTest = satelliteID.to_bytes(6, 'big') + incrementingID.to_bytes(1, 'big')

# Create instances
task = Task(satelliteID, incrementingID, timeLimit=3600)  # Create a Task with a 1-hour limit

# Send a task request
taskID, timeLimit = thread.sendRespond(task)  # Call on the instance
print(f"TaskID: {taskID}, TimeLimit: {timeLimit}")

#send a task respond
taskID, source= thread.sendRespond(task)  # Call on the instance
#####################################################################################################