from CommunicationThread import CommunicationThread
from TaskHandlerThread import TaskHandlerThread
from MissionThread import MissionThread
from OrbitalPositionThread import OrbitalPositionThread
from getmac import get_mac_address
from pathlib import Path
import json


satelliteID = int(get_mac_address().replace(":",""),16)
print(satelliteID)

if satelliteID != 273270825686681:
    from ObjectDetectionThread import ObjectDetectionThread

current_dir = Path(__file__).parent.resolve()
cv_model_path = current_dir / "models" / "yolov8m_best.engine"
image_path = current_dir / "images"
config_path = current_dir / "config_test.JSON"

with open(config_path, 'r') as config_file:
    loaded_config_file = json.load(config_file)
    print(f"Config_file = {loaded_config_file}")

communicationThread = None

orbitalPositionThread = OrbitalPositionThread(config=loaded_config_file,
                                                  tickRate=1.0,
                                                  satelliteID=satelliteID)

taskHandlerThread = TaskHandlerThread(communicationThread=communicationThread, orbitalPositionThread=orbitalPositionThread)


if satelliteID != 273270825686681:
    objectDetectionThread = ObjectDetectionThread(cv_model_path, 
                                              communicationThread = communicationThread, 
                                              taskHandlerThread = taskHandlerThread)

communicationThread = CommunicationThread(satelliteID=satelliteID, 
                                              config=loaded_config_file,
                                              taskHandlerThread=taskHandlerThread, orbitalPositionThread=orbitalPositionThread
                                              )

taskHandlerThread.communicationThread = communicationThread
if satelliteID != 273270825686681:
    objectDetectionThread.communicationThread = communicationThread

missionThread = MissionThread(configPath=config_path,
                              satelliteID=satelliteID,
                              orbitalPositionThread=orbitalPositionThread,
                              taskHandlerThread=taskHandlerThread,
                              imagePath=image_path)

print("Startin orbitlal thread")
orbitalPositionThread.start()
print("Starting communication thread")
communicationThread.start()
print("Starting taskhandler")
taskHandlerThread.start()
print("Starting mission thread")
missionThread.start()
if satelliteID != 273270825686681:
    print("Starting ObjectDetection thread")
    objectDetectionThread.start()
