import socket
import time
import cv2
from pickle import dumps
from Task import Task  # Assuming Task is the class you want to use for the payload
from MessageClasses import ImageDataMessage  # Import the message class
from PIL import Image

# Constants
SERVER_IP = "127.0.0.1"  # Replace with the server IP if it's not localhost
SERVER_PORT = 4500       # Listening port of the server (same as ListeningThread port)

# Create a Task object as the payload for the ImageDataMessage
unix_time_limit = time.time() + 60  # Current time + 60 seconds
task_id = 42  # Example task ID
# You need to create a Task instance with some data (file, image, location, etc.)
# Path to the image you want to send
image_path = '/Users/tobiaslundgaard/Desktop/Semester 5/Projekt5/test.jpg'
task = Task(satelliteID=1, taskCount=task_id, timeLimit=60)



# Load and encode the image as bytes
def load_image_as_bytes(image_path):
    image = cv2.imread(image_path)
    _, encoded_image = cv2.imencode('.jpg', image)  # Encode image as JPEG
    print(encoded_image)
    return encoded_image.tobytes()

# Get the image data in bytes
image_data = load_image_as_bytes(image_path)

# Create the ImageDataMessage with Task as payload and a firstHopID
first_hop_id = 100  # Example of a first hop ID (could be the satellite ID or other identifier)
image_message = ImageDataMessage(payload=task, firstHopID=first_hop_id)

# Serialize the message
serialized_message = dumps(image_message)

# Send the message via UDP socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        # Send the ImageDataMessage containing the Task and image data
        client_socket.sendto(serialized_message, (SERVER_IP, SERVER_PORT))
        print(f"Sent ImageDataMessage with TaskID {task_id} and firstHopID {first_hop_id} to {SERVER_IP}:{SERVER_PORT}")
        
        # Send the image data as a separate message (if needed)
        client_socket.sendto(image_data, (SERVER_IP, SERVER_PORT))
        print(f"Sent image data to {SERVER_IP}:{SERVER_PORT}")

except Exception as e:
    print(f"Error sending message: {e}")
