from Task import Task
from typing import Optional, Union
from threading import Lock

class PriorityQueue:
    """PriorityQueue that handles tasks

    Args:
        None:
    
    """
    def __init__(self):
        self.__queue: list[list[Union[Task, float]]] = []
        self.lock: Lock = Lock()
        

    def addTaskToQueue(self, task:Task, frequency: float = 0.0) -> None:
        """Method that adds task to queue

        Args:
            task (Task): Task that has to be added to queue

        Returns:
            None:
        
        """
        self.__queue.append([task, frequency])
    
    def isEmpty(self) -> bool:
        """Method that checks if queue is empty

        Args:
            None:

        Returns:
            isEmpty (bool): True if queue is empty
        
        """
        if len(self.__queue) == 0:
            return True
        else:
            return False

    def nextTaskNonRemoving(self) -> Optional[list[Union[Task, float]]]:
        """Method for getting the next task in the queue but does not remove the task from the queue

        Args:
            None:
        
        Returns:
            task (Task): The next task in queue
        
        """
        if not self.isEmpty():
            print(self.__queue[0][0])
            min_limit:float = self.__queue[0][0].getUnixTimestampLimit()
            next_task = self.__queue[0]
            next_task_index = 0
            for i in range(len(self.__queue)):
                if self.__queue[i][0].getUnixTimestampLimit() < min_limit:
                    min_limit = self.__queue[i][0].getUnixTimestampLimit()
                    next_task = self.__queue[i]
                    next_task_index = i
            
            return next_task
        else:
            return None
    
    def nextTask(self) -> Optional[list[Union[Task, float]]]:
        """Get the next task of queue. Also removes the task from the queue

        Returns:
            Optional[list[Task, int]]: The list containing the task as well as the frequency
        """
        self.lockQueue()
        task = self.nextTaskNonRemoving()
        
        if task == None:
            return None
        
        self.__queue.remove(task)
        self.releaseQueue()
        return task
    
    def updateFrequencies(self, frequencies: list[float]) -> None:
        self.sortQueue()
        for i in range(len(frequencies)):
            self.__queue[i][1] = frequencies[i]
    
    def sortQueue(self) -> None:
        self.__queue = sorted(self.__queue, key=lambda task: task[0].getUnixTimestampLimit())
    
    def getSortedQueueList(self) -> list[list[Union[Task, float]]]:
        self.sortQueue()
        return self.__queue
    
    def getQueue(self) -> list[list[Union[Task, float]]]:
        return self.__queue
    
    def lockQueue(self) -> None:
        self.lock.acquire()
    
    def releaseQueue(self) -> None:
        self.lock.release()

    def printQueue(self):
        print(self.__queue)


if __name__ == "__main__":
    from random import randint
    queue = PriorityQueue()

    for i in range(3):
        queue.addTaskToQueue(Task(1,i, randint(1,20)))
    
    queue.printQueue()

    task = queue.nextTask()

    queue.printQueue()