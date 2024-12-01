from Task import Task
from typing import List, Optional

class PriorityQueue:
    """PriorityQueue that handles tasks

    Args:
        None:
    
    """
    __queue:List[list[Task, float]] = []

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
            min_limit:float = self.__queue[0].getUnixTimestampLimit()
            for task in self.__queue:
                if task.getUnixTimestampLimit() < min_limit:
                    min_limit = task.getUnixTimestampLimit()
                    next_task:Task = task
                    self.__queue.remove(task)
            return next_task
        else:
            return None
    
    def getSortedQueueList(self) -> List[list[Task, float]]:
        return sorted(self.__queue, key=lambda task: task[0].getUnixTimestampLimit())


if __name__ == "__main__":
    from random import randint
    queue = PriorityQueue()

    for i in range(50):
        queue.addTaskToQueue(Task(1,i, randint(1,20)))
    
    sorted_queue = queue.getSortedQueueList()
    
    for i in sorted_queue:
        print(i[0].getUnixTimestampLimit(), i[1])
