from CommunicationThread import CommunicationThread
from TaskHandlerThread import TaskHandlerThread
from MissionThread import MissionThread
from Task import Task
from ObjectDetectionThread import ObjectDetectionThread
from OrbitalPositionThread import OrbitalPositionThread
from getmac import get_mac_address
from pathlib import Path
import json
import pstats


satelliteID = int(get_mac_address("usb0").replace(":",""),16)
print(satelliteID)
current_dir = Path(__file__).parent.resolve()
cv_model_path = current_dir / "models" / "yolov8m_best.engine"
image_path = current_dir / "images"
config_path = current_dir / "config_test.JSON"

communicationThread = None

taskHandlerThread = TaskHandlerThread(communicationThread=communicationThread)

with open(config_path, 'r') as config_file:
    loaded_config_file = json.load(config_file)

objectDetectionThread = ObjectDetectionThread(cv_model_path, 
                                              communicationThread = communicationThread, 
                                              taskHandlerThread = taskHandlerThread)

communicationThread = CommunicationThread(satelliteID=satelliteID, 
                                              config=loaded_config_file,
                                              taskHandlerThread=taskHandlerThread,
                                              )
orbitalPositionThread = OrbitalPositionThread(config=loaded_config_file,
                                                  tickRate=1.0,
                                                  satelliteID=satelliteID)

missionThread = MissionThread(configPath=config_path,
                              satelliteID=satelliteID,
                              orbitalPosistionThread=orbitalPositionThread,
                              taskHandlerThread=taskHandlerThread,
                              imagePath=image_path)

print("Starting orbitlal thread")
orbitalPositionThread.start()
print("Starting taskhandler")
taskHandlerThread.start()
print("Starting mission thread")
missionThread.start()
print("Starting ObjectDetection thread")
objectDetectionThread.start()
