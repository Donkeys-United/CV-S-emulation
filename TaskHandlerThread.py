#Libraries
import random, threading, time
from Task import Task
from MessageClasses import *
#from MissionThread import *
from CommunicationThread import CommunicationThread
from PriorityQueue import PriorityQueue
from OrbitalPositionThread import OrbitalPositionThread
from EnergyOptimiser import EnergyOptimiser
from RadioEnergy import RadioEnergy


class TaskHandlerThread(threading.Thread):

    def __init__(self, communicationThread: CommunicationThread, orbitalPositionThread: OrbitalPositionThread, algorithmMode: int):
        super().__init__()
        self.running = True
        self.allocatedTasks: PriorityQueue = PriorityQueue()
        self.__unallocatedTasks: PriorityQueue = PriorityQueue()
        self.communicationThread: CommunicationThread = communicationThread
        self.orbitalPositionThread: OrbitalPositionThread = orbitalPositionThread
        self.energyOptimiser = EnergyOptimiser()
        self.algorithmMode = algorithmMode


    def run(self):
        """
        Method to initiate the different threads in the system(Main loop maybe?)
        """
        while self.running:
            if not self.__unallocatedTasks.isEmpty():
                nextUnallocatedTask = self.__unallocatedTasks.nextTask()
                allocateToSelf = self.allocateTaskToSelf(nextUnallocatedTask[0].getUnixTimestampLimit(), nextUnallocatedTask[0].getSource())
                if allocateToSelf[0] == True:
                    self.allocatedTasks.addTaskToQueue(nextUnallocatedTask[0])
                else:
                    self.sendRequest(nextUnallocatedTask[0])
                    self.communicationThread.giveTask(nextUnallocatedTask[0])
            time.sleep(1)



    def allocateTaskToSelf(self, timeLimitUnixTime: float, taskSource: int) -> Tuple[bool, float]:
        """Function check wether a task should be allocated to the current satellite as well as determines the frequency it should run at.

        Args:
            timeLimitUnixTime (float): The time limit of the new task in unix time
            taskSource (int): The source satellite of the task

        Returns:
            Tuple[bool, float]: Returns true with a optimised frequency if the task should be allocated to self
                                Returns false with a frequency of 0 if the task should not be allocated to self
        """
        #Check algorithm mode and if everything should be routed to ground
        if self.algorithmMode == 3:
            return (False, 0.0)
            
        #Lock the queues so they cant be modified during this process
        self.allocatedTasks.lockQueue()
        self.communicationThread.acceptedRequestsQueue.lockQueue()
        
        allocatedTasksQueue = self.allocatedTasks.getSortedQueueList()
        acceptedRequestQueue = self.communicationThread.acceptedRequestsQueue.getSortedQueueList()
        
        currentFrequencies = []
        
        #Merge the queues and extract current given frequencies
        timestamp = time.time()
        allocatedAcceptedTasksQueueID = []
        for i in allocatedTasksQueue:
            allocatedAcceptedTasksQueueID.append([i[0].getTaskID(),i[0].getUnixTimestampLimit() - timestamp])
            currentFrequencies.append(i[1])
        
        for i in acceptedRequestQueue:
            allocatedAcceptedTasksQueueID.append([i[0].getTaskID(), i[0].getUnixTimestampLimit() - timestamp])
            currentFrequencies.append(i[1]) 
        
        #Calculate the current estimate
        currentEnergyEstimate = self.energyOptimiser.totalEnergy(currentFrequencies)
        
        #Sort the tasks based on time limit
        allocatedAcceptedTasksQueueID.append([0, timeLimitUnixTime-timestamp])
        allocatedAcceptedTasksQueueID = sorted(allocatedAcceptedTasksQueueID, key=lambda list: list[1])
        
        #Extract the time limits
        timeLimits = [i[1] for i in allocatedAcceptedTasksQueueID]
        
        #Optimise for energy consumption
        result = self.energyOptimiser.minimiseEnergyConsumption(timeLimits, 0)
        
        #Check if a time limit was exceeded
        if not result.success and self.algorithmMode == 1:
            return False, 0.0
        
        #Extract the optimised frequencies
        optimisedFrequencies = result.x
        
        #Estimate the optimised energy consumption
        optimisedEnergyEstimate = self.energyOptimiser.totalEnergy(optimisedFrequencies)
        
        #Check whether transmitting to ground station would be more efficient
        if optimisedEnergyEstimate - currentEnergyEstimate > self.estimateTransmissionEnergyToGround(taskSource) and self.algorithmMode == 1:
            return False, 0.0
        
        #Split the queues again
        allocatedTaskOptimisedFreq = []
        acceptedTaskOptimisedFreq = []
        allocatedTaskID = {task[0].getTaskID() for task in allocatedTasksQueue}
        
        for (taskID, _), frequency in zip(allocatedAcceptedTasksQueueID, optimisedFrequencies):
            if taskID == 0:
                newTaskOptimisedFrequency = frequency
            elif taskID in allocatedTaskID:
                allocatedTaskOptimisedFreq.append(frequency)
            else:
                acceptedTaskOptimisedFreq.append(frequency)
        
        #Update the frequencies
        self.allocatedTasks.updateFrequencies(allocatedTaskOptimisedFreq)
        self.communicationThread.acceptedRequestsQueue.updateFrequencies(acceptedTaskOptimisedFreq)
        
        #Release the queues
        self.allocatedTasks.releaseQueue()
        self.communicationThread.acceptedRequestsQueue.releaseQueue()
        
        #Return True plus the optimised frequency for the new tasks
        return True, newTaskOptimisedFrequency
        
        
        # This must not be deleted :)
        # trueFalseMethod = random.choice([True, False])
        # if trueFalseMethod == True:
        #     return True
        # else: 
        #     return False
        

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

        # Add the message to the CommunicationThread #Der var en nisse her
        self.communicationThread.addTransmission(sendRequestMessage)

        # Return the task ID and time limit
        #return sendRequestMessage.getTaskID(), sendRequestMessage.getUnixTimeLimit()



    def sendRespond(self, message: RequestMessage):
        """
        Method to send a respond to other satellites telling them they can perform the requested task
        """
        taskID = message.getTaskID()
        sendRespondMessage = RespondMessage(
            taskID=taskID,
            source=int.from_bytes(taskID[0:6], byteorder='big'),
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
        return len(self.allocatedTasks) + self.communicationThread.getTotalAcceptedTasks()


    def appendTask(self, task: Task, frequency: float):
        """Append a task to the allocatedTasks queue 

        Args:
            task (Task): Task to be added to the queue
        """
        self.allocatedTasks.addTaskToQueue(task, frequency)
    
    def appendUnallocatedTask(self, task: Task):
        self.__unallocatedTasks.addTaskToQueue(task)
    
    def estimateTransmissionEnergyToGround(self, taskSource: int) -> float:
        """Estimate the energy consumed for transmitting directly to ground

        Args:
            taskSource (int): The source of the task

        Returns:
            float: The estimated energy
        """        
        numberOfSatHops, satDist, groundDist = self.orbitalPositionThread.getPathDistanceToGround(taskSource)
        energy = numberOfSatHops * RadioEnergy.getEnergyForTransmission(self.orbitalPositionThread.neighbourSatDist, 6*10**6) + RadioEnergy.getEnergyForTransmission(groundDist, 6*10**6)
        return energy

"""
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

""
Generate a random task
""
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
"""
if __name__ == "__main__":
    import json
    from random import randint
    from MessageClasses import RequestMessage
    test_json = """{
    "satellites": [
        {
        "id": 1,
        "ip_address": "192.168.1.101",
        "connections": [1, 4],
        "initial_angle": 0.0
        },
        {
        "id": 2,
        "ip_address": "192.168.1.102",
        "connections": [2,3],
        "initial_angle": 1.5708
        },
        {
        "id": 3,
        "ip_address": "192.168.1.103",
        "connections": [2,3],
        "initial_angle": 3.14159
        },
        {
        "id": 4,
        "ip_address": "192.168.1.104",
        "connections": [3,1],
        "initial_angle": 4.71239
        },
        {
        "id": 5,
        "ip_address": "192.168.1.105",
        "connections": [3,1],
        "initial_angle": 5.71239
        }
    ],
    "altitude": 200000,
    "ground_station_ip": "192.168.1.106"
    }"""
    taskHandler: TaskHandlerThread = None
    loaded_json = json.loads(test_json)
    orbitalPositionThread = OrbitalPositionThread(loaded_json, 5, 1)
    communicationThread = CommunicationThread(1, loaded_json, taskHandler, orbitalPositionThread)
    taskHandler = TaskHandlerThread(communicationThread, orbitalPositionThread)
    
    for i in range(1,11):
        taskHandler.appendTask(Task(1, i, randint(5,20)), 306000000.0)
        
    communicationThread.acceptedRequestsQueue.addMessage(RequestMessage(time.time()+7, 11), 306000000)
    communicationThread.acceptedRequestsQueue.addMessage(RequestMessage(time.time()+11, 12), 306000000)
    
    print(taskHandler.allocateTaskToSelf(time.time() + 9,1))
