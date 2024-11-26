import json
import uuid
import os
import time
import cv2
import numpy as np
import logging
from orbitalPositionThread_test import orbitalPositionThread_test  # External class import
from Task_test import Task  # External class import

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("task_logger.log"),  # Save logs to a file
        logging.StreamHandler()  # Also log to the console
    ]
)

class MissionThread:
    def __init__(self, config_path: str):
        """
        Initialize the MissionThread with configuration data.
        """
        self.config_path = config_path
        self.image_path = r"C:\Users\Phuon\OneDrive\Dokumenter\GitHub\CV-S-emulation\test"
        self.missions = []
        self.my_missions = []
        self.files = []
        self.satelliteID = uuid.getnode()

        logging.info("Initializing MissionThread for satellite ID: %s", self.satelliteID)

        # Check if image directory exists
        if not os.path.exists(self.image_path):
            logging.critical("Image directory not found: %s", self.image_path)
            raise FileNotFoundError(f"Directory not found: {self.image_path}")
        self.files = os.listdir(self.image_path)
        logging.debug("Image files found: %s", self.files)

        # Load and parse JSON configuration
        try:
            with open(self.config_path, 'r') as file:
                config_data = json.load(file)
            self.missions = config_data.get("missions", [])
            logging.info("Configuration loaded successfully from %s", self.config_path)
            logging.debug("Parsed missions: %s", self.missions)
        except Exception as e:
            logging.error("Failed to load configuration: %s", e)
            raise

        # Filter relevant missions
        orbital_thread = orbitalPositionThread_test()
        for mission in self.missions:
            logging.debug("Checking mission: %s", mission)
            if mission.get("satellite_id") == self.satelliteID and orbital_thread.canExecuteMission(
                    mission.get("location_radian"), mission.get("orbit_number")):
                self.my_missions.append(mission)
                logging.info("Mission added: %s", mission)
            else:
                logging.warning("No valid missions found for mission: %s", mission)

    def _create_task(self, time_limit, image_file_path, location):
        """
        Create a task with the given parameters.
        """
        task_mac = uuid.getnode()
        logging.debug("Creating task with task_mac: %s, file: %s, location: %s", task_mac, image_file_path, location)
        task = Task(time_limit)
        image = cv2.imread(image_file_path)

        if image is None:
            logging.warning("Failed to load image: %s", image_file_path)
            return

        task.appendImage(image_file_path, image, location)
        logging.info("Task created for file: %s", image_file_path)

    def run(self):
        """
        Main loop for executing missions.
        """
        try:
            logging.info("Starting mission thread...")
            while True:
                for mission in self.my_missions:
                    logging.debug("Processing mission: %s", mission)
                    satellite_id = mission.get("satellite_id")
                    location_radian = mission.get("location_radian")
                    orbit_number = mission.get("orbit_number")
                    pictures_number = mission.get("pictures_number", 0)
                    time_limit = mission.get("time_limit", 0)

                    if None in (satellite_id, location_radian, orbit_number):
                        logging.error("Invalid mission data: %s", mission)
                        continue

                    # Select random images
                    if pictures_number > len(self.files):
                        logging.error("Not enough images to fulfill mission: %s", mission)
                        continue

                    image_list = np.random.choice(self.files, pictures_number, replace=False)
                    logging.debug("Selected images: %s", image_list)
                    for image in image_list:
                        file = os.path.join(self.image_path, image)
                        self._create_task(time_limit, file, location_radian)

                    logging.info("Mission completed: %s", mission)
                    time.sleep(2)
        except KeyboardInterrupt:
            logging.info("Execution interrupted by user.")
        except Exception as e:
            logging.exception("Unexpected error occurred: %s", e)


# Run the MissionThread
if __name__ == "__main__":
    file_name = r"C:\Users\Phuon\OneDrive\Dokumenter\GitHub\CV-S-emulation\config_test.JSON"
    mission_thread = MissionThread(file_name)
    mission_thread.run()
