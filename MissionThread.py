import json
import logging.config
from OrbitalPositionThread import OrbitalPositionThread # Import the other class
from TaskHandlerThread import TaskHandlerThread
import numpy as np
import os
from Task import Task
import cv2
import logging 
import threading

# Configure logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("task_logger.log"),     # Save logs into a file
        logging.StreamHandler()     # Also log to the console
    ]
)

class MissionThread(threading.Thread):
    taskCounter=0

    def __init__(self, configPath:json, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None, satelliteID: int, orbitalPositionThread: OrbitalPositionThread, taskHandlerThread: TaskHandlerThread, imagePath):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        """
        Initialize the MissionThread with configuration data.
        """
         
        # Instance Attributes
        self.configPath = configPath
        self.IMAGEPATH = imagePath
        self.myMissions = []
        self.files = [] 
        self.satelliteID = satelliteID
        self.orbitalPositionThread = orbitalPositionThread
        self.taskHandlerThread = taskHandlerThread
        self.wait = threading.Event()
    

        logging.info("Initializing MissionThread for satelliteID: %s", self.satelliteID)

        #Check if image directory exist 
        if not os.path.exists(self.IMAGEPATH):
             logging.critical("Image directory does not exist: %s", self.IMAGEPATH)
             raise FileNotFoundError(f"Directory not found {self.IMAGEPATH}")
        self.files = os.listdir(self.IMAGEPATH)
        logging.debug("Image files found: %s", self.files)


        # Load and parse JSON configuration 
        try:
            with open(self.configPath, 'r') as file: 
                configData = json.load(file) # Parsed JSON data as a Python dictionary or list
        except Exception as e:
             logging.error("Failed to load configuration: %s", e)
             raise
         
        # Filter relevant missions 
        for mission in configData.get("missions"): # Extract only the missions data 
             logging.debug("Checking mission: %s", mission)
             if mission.get("satellite_id") == self.satelliteID:
                 self.myMissions.append(mission)
                 logging.info("Mission added: %s", mission)
             else: 
                 logging.warning("No valid missions found for missions: %s", mission)


    # Method

    def __createTask(self, timeLimit, file, location):
        """
        Create a task 
        """
        logging.debug("Creating task with taskMAC: %s, file: %s, location: %s", self.satelliteID, file, location)
        task = Task(self.satelliteID, self.taskCounter, timeLimit)

        # Include a taskCounter
        if self.taskCounter == 255:
            self.taskCounter=0
        else:
            self.taskCounter += 1

        image = cv2.imread(file)

        if image is None:
            logging.warning("Failed to load image: %s", file)
            return

        task.appendImage(file,image,location)
        logging.info("Task created for file: %s", file)

        return task




    def run(self):
        """
        Main loop for executing mission
        """
        try: 
            logging.info("Starting mission thread")
            while True:
                for i in range(len(self.myMissions)):
                    logging.info("Processing mission: %s", self.myMissions[i])
                    
                    location_radian = self.myMissions[i].get("location_radian")
                    orbit_number = self.myMissions[i].get("orbit_number")

                    if self.orbitalPositionThread.canExecuteMission(location_radian, orbit_number):
                        satellite_id = self.myMissions[i].get("satellite_id")
                        pictures_number = self.myMissions[i].get("pictures_number")
                        time_limit = self.myMissions[i].get("time_limit")

                        if None in (satellite_id, location_radian, orbit_number, pictures_number, time_limit):
                            logging.error("Invalid mission data: %s", self.myMissions[i])
                            continue

                        imageList = np.random.choice(self.files, pictures_number, replace = True) #replace change to false, when there is enough images
                        logging.debug("Selected images: %s", imageList)
                        for image in imageList:
                            # Load the image
                            file = os.path.join(self.IMAGEPATH, image)
                            task = self.__createTask(time_limit, file, location_radian)

                            self.taskHandlerThread.appendUnallocatedTask(task)

                    
                        logging.info("Mission append: %s", self.myMissions[i])
                        self.myMissions.pop(i)
                        break
                self.wait.wait(2) #sleep for 2 sec

        except KeyboardInterrupt:  #bare for at stoppe 
            print("Execution interrupted by user.")  
