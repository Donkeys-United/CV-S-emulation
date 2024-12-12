# External library imports
from getmac import get_mac_address
from pathlib import Path
from platform import system
import json
import time

# Internal library imports
from CommunicationThread import CommunicationThread
from TaskHandlerThread import TaskHandlerThread
from MissionThread import MissionThread
from OrbitalPositionThread import OrbitalPositionThread
from PowerMonitorThread import PowerMonitorThread

# Setting MAC adress as satelliteID 
satelliteID = int(get_mac_address().replace(":",""),16)
print(satelliteID)

# Checking which operating system is used.
os = system()

# Importing object detection if device does not use Windows.
if os != "Windows":
    from ObjectDetectionThread import ObjectDetectionThread

# Saving important paths.
current_dir = Path(__file__).parent.resolve()
cv_model_path = current_dir / "models" / "yolov8m_best.engine"
image_path = current_dir / "images"
config_path = current_dir / "config_test.JSON"

# Loading the config file.
with open(config_path, 'r') as config_file:
    loaded_config_file = json.load(config_file)
    print(f"Config_file = {loaded_config_file}")

# Placeholder communicationThread - avoids circular imports.
communicationThread = None

# Setting up Orbital Position Thread.
orbitalPositionThread = OrbitalPositionThread(config=loaded_config_file,
                                                  tickRate=1.0,
                                                  satelliteID=satelliteID)

# Setting up Task Handler Thread.
taskHandlerThread = TaskHandlerThread(communicationThread=communicationThread, orbitalPositionThread=orbitalPositionThread)

# Setting up Object Detection Thread - if OS is not Windows.
if os != "Windows":
    objectDetectionThread = ObjectDetectionThread(cv_model_path, 
                                              communicationThread = communicationThread, 
                                              taskHandlerThread = taskHandlerThread)

# Setting up real Communication Thread.
communicationThread = CommunicationThread(satelliteID=satelliteID, 
                                              config=loaded_config_file,
                                              taskHandlerThread=taskHandlerThread, orbitalPositionThread=orbitalPositionThread
                                              )

# Replaing placeholder Communication Thread with Real Communication Thread.
taskHandlerThread.communicationThread = communicationThread
if os != "Windows":
    objectDetectionThread.communicationThread = communicationThread

# Setting up Mission Thread
missionThread = MissionThread(configPath=config_path,
                              satelliteID=satelliteID,
                              orbitalPositionThread=orbitalPositionThread,
                              taskHandlerThread=taskHandlerThread,
                              imagePath=image_path)

for satellite in loaded_config_file["satellites"]:
    if satellite["id"] == satelliteID:
        isNano = satellite["is_nano"]

powerMonitorThread = PowerMonitorThread(measuringIntervalms=40, 
                                        emulationRunName=loaded_config_file["emulation_run_name"], 
                                        unixtimeStart=time.time(), 
                                        notes=None, 
                                        isNano=isNano, 
                                        transmissionThread=communicationThread.transmissionThread, 
                                        satelliteDistance=orbitalPositionThread.neighbourSatDist)


# Starting all threads.
print("Startin orbitlal thread")
orbitalPositionThread.start()
print("Starting communication thread")
communicationThread.start()
print("Starting taskhandler")
taskHandlerThread.start()
print("Starting mission thread")
missionThread.start()
print("Starting power monitor thread")
powerMonitorThread.start()
if os != "Windows":
    print("Starting ObjectDetection thread")
    objectDetectionThread.start()
