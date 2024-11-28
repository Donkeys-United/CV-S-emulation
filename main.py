from CommunicationThread import CommunicationThread
from TaskHandlerThread import TaskHandlerThread
from MissionThread import MissionThread
from Task import Task
from ObjectDetectionThread import ObjectDetectionThread
from OrbitalPositionThread import OrbitalPositionThread
from uuid import getnode
from pathlib import Path

satelliteID = getnode()

current_dir = Path(__file__).parent.resolve()
cv_model_path = current_dir / "models" / "yolov8m_best.pt"
image_path = current_dir / "images"
config_path = current_dir / "config_test.JSON"

communicationThread = None

taskHandlerThread = TaskHandlerThread(communicationThread=communicationThread)

with open(config_path, 'r') as config_file:
    communicationThread = CommunicationThread(satelliteID=satelliteID, 
                                              config=config_file,
                                              taskHandlerThread=taskHandlerThread,
                                              )
    orbitalPositionThread = OrbitalPositionThread(config=config_file,
                                                  tickRate=1.0)

missionThread = MissionThread(configPath=config_path,
                              satelliteID=satelliteID,
                              orbitalPosistionThread=orbitalPositionThread,
                              taskHandlerThread=taskHandlerThread)

objectDetectionThread = ObjectDetectionThread(cv_model_path, 
                                              communicationThread = communicationThread, 
                                              taskHandlerThread = taskHandlerThread)


