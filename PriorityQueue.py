from Task import Task
from typing import List, Optional

class PriorityQueue:
    """PriorityQueue that handles tasks

    Args:
        None:
    
    """
    __queue:List[Task] = []

    def addTaskToQueue(self, task:Task) -> None:
        """Method that adds task to queue

        Args:
            task (Task): Task that has to be added to queue

        Returns:
            None:
        
        """
        self.__queue.append(task)
    
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

    def nextTask(self) -> Optional[Task]:
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
