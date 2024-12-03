from Task import Task
from typing import List, Optional

class PriorityQueue:
    """PriorityQueue that handles tasks

    Args:
        None:
    
    """
    def __init__(self):
        self.__queue: list[list[Task, float]] = []

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

    def nextTask(self) -> Optional[list[Task, float]]:
        """Method for getting the next task in the queue. Method removes the task retrieved

        Args:
            None:
        
        Returns:
            task (Task): The next task in queue
        
        """
        if not self.isEmpty():
            min_limit:float = self.__queue[0][0].getUnixTimestampLimit()
            next_task = self.__queue[0]
            next_task_index = 0
            for i in range(len(self.__queue)):
                if self.__queue[i][0].getUnixTimestampLimit() < min_limit:
                    min_limit = self.__queue[i][0].getUnixTimestampLimit()
                    next_task = self.__queue[i]
                    next_task_index = i
            
            self.__queue.pop(next_task_index)
            return next_task
        else:
            return None
    
    def getSortedQueueList(self) -> List[list[Task, float]]:
        return sorted(self.__queue, key=lambda task: task[0].getUnixTimestampLimit())

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