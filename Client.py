import socket, time
from pickle import dumps
from MessageClasses import RequestMessage

# Constants
SERVER_IP = "127.0.0.1"  # Replace with the server IP if it's not localhost
SERVER_PORT = 4500       # Listening port of the server (same as ListeningThread port)

# Create a message instance
unix_time_limit = time.time() + 60  # Current time + 60 seconds
task_id = 42  # Example task ID
message = RequestMessage(
    unixTimeLimit=unix_time_limit, 
    taskID=task_id)

# Serialize the message
serialized_message = dumps(message)

# Send the message via UDP socket
try:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.sendto(serialized_message, (SERVER_IP, SERVER_PORT))
        print(f"Sent RequestMessage with TaskID {task_id} to {SERVER_IP}:{SERVER_PORT}")
except Exception as e:
    print(f"Error sending message: {e}")
