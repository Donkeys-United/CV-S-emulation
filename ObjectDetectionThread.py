from ultralytics import YOLO
from MessageClasses import ImageDataMessage, ProcessedDataMessage
import CommunicationThread
import os
from pathlib import Path
import Task


class ObjectDetectionThread:
    """ Class used for running inference on images, using a YOLOv8 model.
    """

    def __init__(self, PATH_TO_MODEL):
        self.PATH_TO_MODEL = PATH_TO_MODEL
        self.model = self.loadModel()
    
    def loadModel(self):
        """Method which is automatically called when ObjectDetectionThread 
        object instance is initialised. This way, the correct model is loaded when initialising the object instance.

        Returns:
            YOLO: a YOLO object instance, using the model specified by PATH_TO_MODEL.
        """
        model = YOLO(self.PATH_TO_MODEL)
        return model
    
    def runInference(self, imageObject: Task):
        """Method used for running inference on a specific imageDataMessage object instance - which the satellite would have received or captured itself.

        Args:
            imageObject (ImageDataMessage): the object instance containing the image, which is to be the subject of the inference.

        Returns:
            ProcessedDataMessage: a object instance, ready to be sent to the ground station, with the results of the inference.
        """
        image = imageObject.getImage()
        results = self.model.predict(image, 
                                    save = True, 
                                    show_labels = True, 
                                    show_boxes = True, 
                                    show_conf = True)
        bounding_boxes = [result.boxes for result in results]
        bounding_box_xyxy = [box.xyxy for box in bounding_boxes]

        save_dir = results[0].save_dir

        image_name_list = []

        # Rename saved files (example logic)
        for image_path in Path(save_dir).glob("*.jpg"):  # Adjust extension if not .jpg
            new_name = f"processed_{image_path.stem}.jpg"
            image_name_list.append(f"{save_dir}/{new_name}")
            os.rename(image_path, save_dir / new_name)

        finished_message_list = []
        for result in len(results):
            finished_message_list.append(ProcessedDataMessage(image_name_list[result], imageObject.getLocation(), imageObject.getUnixTimeStamp(), imageObject.getFileName(), ((bounding_box_xyxy[result][0], bounding_box_xyxy[result][1]),(bounding_box_xyxy[result][2], bounding_box_xyxy[result][4]))))
        return finished_message_list

    def sendProcessedDataMessage(message_list: list[ProcessedDataMessage], communication_thread: CommunicationThread):
        """Simple method for moving the PrcessedDataMessage object instance to the transmission queue in the CommunicationThread object instance.

        Args:
            message (ProcessedDataMessage): the ProcessedDataMessage object instance returned by the runInference method.
            communication_thread (CommunicationThread): the CommunicationThread object instance used by the communication thread.

        Returns:
            None: none
        """
        for message in message_list:
            communication_thread.transmissionQueue.append(message)
        return None
