from ultralytics import YOLO
from torch import device
from MessageClasses import ImageDataMessage, ProcessedDataMessage
from CommunicationThread import CommunicationThread
from TaskHandlerThread import TaskHandlerThread
import os
from pathlib import Path, PurePath
from Task import Task
import threading
import subprocess
import torch


class ObjectDetectionThread(threading.Thread):
    """ Class used for running inference on images, using a YOLOv8 model.
    """

    def __init__(self, PATH_TO_MODEL, communicationThread: CommunicationThread, taskHandlerThread: TaskHandlerThread):
        super().__init__()
        self.PATH_TO_MODEL = PATH_TO_MODEL
        self.FREQUENCY_PATH = "/sys/devices/platform/17000000.gpu/devfreq/17000000.gpu/"
        self.SUDO_PASSWORD = "1234"
        self.AVAILABLE_FREQUENCIES = [306000000, 408000000, 510000000, 612000000,642750000]
        self.model = self.loadModel()
        self.communicationThread = communicationThread
        self.taskHandlerThread = taskHandlerThread
        self._stop_event = threading.Event()
        self.no_tasks = threading.Event()
        dummy_input = torch.rand(1, 3, 640, 640).to('cuda')
        self.model.predict(dummy_input)
    
    def loadModel(self):
        """Method which is automatically called when ObjectDetectionThread 
        object instance is initialised. This way, the correct model is loaded when initialising the object instance.

        Returns:
            YOLO: a YOLO object instance, using the model specified by PATH_TO_MODEL.
        """
        model = YOLO(self.PATH_TO_MODEL)
        return model
    
    def runInference(self, TaskFrequencyList: list[Task, float]):
        """Method used for running inference on a specific imageDataMessage object instance - which the satellite would have received or captured itself.

        Args:
            imageObject (ImageDataMessage): the object instance containing the image, which is to be the subject of the inference.

        Returns:
            ProcessedDataMessage: a object instance, ready to be sent to the ground station, with the results of the inference.
        """
        
        imageObject = TaskFrequencyList[0]
        
        image = imageObject.getImage()
        """
        results = self.model.predict(image, 
                                    save = True, 
                                    show_labels = True, 
                                    show_boxes = True, 
                                    show_conf = True,
                                    device=0)
        """

        results = self.model.predict(image, device=0)
        for result in results:
            result.save_crop(save_dir=result.save_dir)

        save_dir = Path(results[0].save_dir)
        
        bounding_box_list = result.boxes.xyxy.tolist()
        #print(f"\n\nBounding Box List: {bounding_box_list}")

        image_name_list = []
        short_name_list = []

        image_file_name = PurePath(imageObject.getFileName()).name

        crop_number = 0

        # Rename saved files (example logic)
        for image_path in Path(save_dir / "boat").glob("*.jpg"):  # Adjust extension if not .jpg
            if not image_path.name.startswith("processed_"):
                new_name = f"processed_{crop_number}_{image_file_name}"
                image_name_list.append(str(save_dir / "boat" / new_name))
                image_path.rename(save_dir / "boat" / new_name)
                short_name_list.append(PurePath(image_name_list[-1]).name)
                crop_number += 1
        

        finished_message_list = []
        for result in range(len(image_name_list)):
            #print(f"\n Results Lenght: {result}")
            #print(short_name_list[result])
            finished_message_list.append(ProcessedDataMessage(image_name_list[result], 
                                                              imageObject.getLocation(), 
                                                              imageObject.getUnixTimestamp(), 
                                                              short_name_list[result], 
                                                              bounding_box_list,
                                                              firstHopID=201170498634677))
        return finished_message_list
    
    def changeFrequency(self, frequency: float) -> None:
        """This function fixes the gpu at the closest frequency available to the input frequency
        Args:
            frequency (float): The desired frequency
        """
        frequencies = [f for f in self.AVAILABLE_FREQUENCIES if f >= frequency]
        command = (
            'echo 1234 | sudo -S sh -c "cd /sys/devices/platform/17000000.gpu/devfreq/17000000.gpu && '
            'echo 306000000 | tee min_freq max_freq"'
        )
        subprocess.run(
            command, shell=True
        )

    def sendProcessedDataMessage(self, message_list: list[ProcessedDataMessage]):
        """Simple method for moving the PrcessedDataMessage object instance to the transmission queue in the CommunicationThread object instance.

        Args:
            message (ProcessedDataMessage): the ProcessedDataMessage object instance returned by the runInference method.
            communication_thread (CommunicationThread): the CommunicationThread object instance used by the communication thread.

        Returns:
            None: none
        """
        for message in message_list:
            self.communicationThread.addTransmission(message)
        return None

    def run(self):
        # Det her skal ændres, således at der er en metode i stedet for at læse direkte fra __allocatedTasks
        while not self._stop_event.is_set():
            if not self.taskHandlerThread.allocatedTasks.isEmpty():
                print("Running Object detection")
                processedDataList = self.runInference(self.taskHandlerThread.allocatedTasks.nextTask())
                self.sendProcessedDataMessage(processedDataList)
            else:
                #Set the gpu frequency to smallest possible frequency to save on power
                #self.changeFrequency(self.AVAILABLE_FREQUENCIES[0])
                self.no_tasks.wait(1)


    def stop(self):
        self._stop_event.set()
"""        
if __name__ == "__main__":
    import cv2
    current_dir = Path(__file__).parent.resolve()
    cv_model_path = current_dir / "models" / "yolov8m_best.pt"
    taskHandler = TaskHandlerThread(None) 
    objectThread = ObjectDetectionThread(cv_model_path,None,taskHandler)
    task = Task(1,1,10)
    image_dir = current_dir / "images" / "GE_1_jpg.rf.4247084b7a777fee8a12057bce802026.jpg"
    task.appendImage("GE_1_jpg.rf.4247084b7a777fee8a12057bce802026.jpg",cv2.imread(image_dir), 0 + 0j)
    taskHandler.allocatedTasks.addTaskToQueue(task)
    objectThread.start()
"""