from Task import Task
from typing import List, Optional

class PriorityQueue:
    __queue:List[Task] = []

    def addTaskToQueue(self, task:Task) -> None:
        self.__queue.append(task)
    
    def isEmpty(self) -> bool:
        if len(self.__queue) == 0:
            return True
        else:
            return False

    def nextTask(self) -> Optional[Task]:
        if not self.isEmpty():
            min_limit:float = self.__queue[0].getUnixTimestampLimit()
            for task in self.__queue:
                if task.getUnixTimestampLimit() < min_limit:
                    min_limit = task.getUnixTimestampLimit()
                    next_task:Task = task
            return next_task
        else:
            return None
