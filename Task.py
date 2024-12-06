
from numpy import ndarray
import time

class Task:
    """Task that stores the information that has to be processed by the system

    Args:
        satelliteID (int): The local satellite id
        taskCount (int): The task number that appends to the id of a task
        timeLimit (int): The time that a task should be processed within
    
    """

    taskID:bytes
    fileName:str
    location:complex
    unixTimestamp:float
    unixTimestampLimit:float
    image:ndarray


    def __init__(self, satelliteID:int, taskCount:int, timeLimit:int) -> None:
        self.taskID =  taskCount.to_bytes(1, 'big') + satelliteID.to_bytes(6, 'big') 
        self.unixTimestamp = time.time()
        self.unixTimestampLimit = self.unixTimestamp + timeLimit

    def appendImage(self, fileName:str, image: ndarray, location:complex) -> None:
        """Method for adding image data to Task

        Args:
            fileName (str): File name
            image (ndarray): Numpy array with image data
            location (complex): location where the image is taken
        
        Returns:
            None:
        
        """
        self.fileName = fileName
        self.image = image
        self.location = location
    

    def getTaskID(self) -> bytes:
        """Returns taskID

        Args:
            None:
        
        Returns:
            taskID (bytes): Returns the taskID
        
        """
        return self.taskID
    
    def getFileName(self) -> str:
        """Returns fileName

        Args:
            None:
        
        Returns:
            fileName (str): Returns fileName
        
        """
        return self.fileName
    
    def getLocation(self) -> complex:
        """Returns location

        Args:
            None:
        
        Returns:
            location (complex): Returns location
        
        """
        return self.location
    
    def getUnixTimestamp(self) -> float:
        """Returns unixTimestamp

        Args:
            None:
        
        Returns:
            unixTimestamp (float): Returns unixTimestamp
        
        """
        return self.unixTimestamp
    
    def getUnixTimestampLimit(self) -> float:
        """Returns unixTimestampLimit

        Args:
            None:
        
        Returns:
            unixTimestampLimit (float): Returns unixTimestampLimit
        
        """
        return self.unixTimestampLimit
    
    def getImage(self) -> ndarray:
        """Returns image data

        Args:
            None:
        
        Returns:
            image (ndarray): Returns image data
        
        """
        return self.image
    
    def getSource(self) -> int:
        """Returns source of task creation

        Args:
            None:
        
        Returns:
            source (int): Returns source
        
        """
        return int.from_bytes(self.getTaskID()[-6:], "big")