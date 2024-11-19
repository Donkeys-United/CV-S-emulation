from ultralytics import YOLO
import ImageDataMessage, ProcessedDataMessage, CommunicationThread


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
    
    def runInference(self, imageObject: ImageDataMessage):
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

        # Mangler måde at pakke det om til ProcessedDataMessage - Class ikke lavet endnu.
        finished_message = ProcessedDataMessage
        return finished_message

    def sendProcessedDataMessage(message: ProcessedDataMessage, communication_thread: CommunicationThread):
        """Simple method for moving the PrcessedDataMessage object instance to the transmission queue in the CommunicationThread object instance.

        Args:
            message (ProcessedDataMessage): the ProcessedDataMessage object instance returned by the runInference method.
            communication_thread (CommunicationThread): the CommunicationThread object instance used by the communication thread.

        Returns:
            None: none
        """
        communication_thread.transmissionQueue.append(message)
        return None
