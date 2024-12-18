import MessageClasses
import Task
from pathlib import Path
import cv2
from pickle import dumps
from pympler import asizeof
import numpy as np
import os


current_dir = Path(__file__).parent.resolve()
image_path = current_dir / "images" / "GE_165_jpg.rf.e7cb4fa72922c60b3ca23e70d2b7b672.jpg"
image1 = cv2.imread(image_path)

image2_source = open(image_path, 'rb')
image2 = image2_source.read()

task = Task.Task(0, 1, 1)
task.appendImage("GE_165_jpg.rf.e7cb4fa72922c60b3ca23e70d2b7b672.jpg", image1, 0)
message1 = MessageClasses.ImageDataMessage(task, 1)

pickled_message1 = dumps(message1)
pickled_message2 = dumps(image1)
#pickled_message3 = dumps(image2)

print(f"Object message size = {asizeof.asizeof(message1)}")
print(f"Object message pickled = {len(pickled_message1)}")
print(f"Image ndarray message size = {asizeof.asizeof(image1)}")
print(f"Image ndarray message pickled= {len(pickled_message2)}")
print(f"Image Only message = {len(image2)}")

