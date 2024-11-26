import CommunicationThread, TaskHandlerThread, MissionThread, Task
from uuid import getnode

satelliteID = getnode()

communicationThread = CommunicationThread.CommunicationThread()

taskHandlerThread = TaskHandlerThread.TaskHandlerThread()

missionThread = MissionThread.MissionThread()


task_1 = Task.Task(satelliteID, 1, 10)
