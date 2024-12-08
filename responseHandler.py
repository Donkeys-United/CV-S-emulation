from threading import Thread
from MessageClasses import RespondMessage, ImageDataMessage
from OrbitalPositionThread import OrbitalPositionThread
from typing import List, Union, Dict
from Task import Task
import time



class ResponseHandler(Thread):
    responses: List[dict] = []

    def __init__(self, communicationThread, orbitalPosistionThread):
        super().__init__()
        self.communicationThread = communicationThread
        self.orbitalPositionThread = orbitalPosistionThread

    def run(self):
        while True:
            self.decrementTime()
            time.sleep(0.1)
        

    def addTask(self, task: Task) -> None:
        """Method for adding a new task to CommunicationThread

        Args:
            task (Task): Task to be added to CommunicationThread

        Returns:
            None:
        
        """
        responseTimeLimit = (task.unixTimestampLimit - time.time()) * 0.2
        response_dict = {"task": task,
                         "timeLimit": responseTimeLimit,
                         "responseMessages": []}
        self.responses.append(response_dict)
    

    def decrementTime(self) -> None:
        """Method for decreasing the responseTimeLimit

        Args:
            None:
        
        Returns:
            None:
        
        """
        for i in self.responses:
            if not i['timeLimit'] <= 0:
                i['timeLimit'] -= 0.1
            else:
                if len(i["responseMessages"]) == 1:
                    task = i["task"]
                    firstHopID = i["responseMessages"][0].getLastSenderID
                    dataPacket = ImageDataMessage(payload=task, firstHopID=firstHopID)
                    self.communicationThread.transmissionQueue.append(dataPacket)
                elif len(i["responseMessages"]) == 0:
                    task = i["task"]
                    firstHopID_1 = self.communicationThread.connectionsIP[0]
                    firstHopID_2 = self.communicationThread.connectionsIP[1]
                    dataPacket = ImageDataMessage(payload=task, firstHopID=firstHopID_2)
                    self.communicationThread.transmissionQueue.append(dataPacket)
                    dataPacket = ImageDataMessage(payload=task, firstHopID=firstHopID_1)
                    self.communicationThread.transmissionQueue.append(dataPacket)
    
    def addResponse(self, response: RespondMessage) -> None:
        taskID = response.getTaskID()
        for task_dict in self.responses:
            task = task_dict["task"]
            if task.getTaskID() == taskID:
                task_dict["responseMessages"].append(response)
                if len(task_dict["responseMessages"]) == 2:
                    firstHopID = self.getPriority(task_dict["responseMessages"])
                    task_ref = task_dict["task"]
                    dataPacket = ImageDataMessage(payload=task_ref, firstHopID=firstHopID)
                    self.communicationThread.transmissionQueue.append(dataPacket)


    def getPriority(self, responseList: List):
        priorityList = self.orbitalPositionThread.getSatellitePriorityList()
        source1 = responseList[0].getSource()
        source2 = responseList[1].getSource()

        for priority in priorityList:
            if priority == source1:
                firstHopID = responseList[0].getLastSenderID()
            elif priority == source2:
                firstHopID = responseList[1].getLastSenderID()
        return firstHopID


