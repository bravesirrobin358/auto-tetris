import threading
import base64
import cv2
import numpy as np
import requests
import asyncio
import aiohttp


def request_inference(base64_image: str, model):
    """
    Uses a YOLO model to detect a person in the image and returns 'left', 'right', or 'middle'
    based on the person's center relative to the image width. Assumes one human in the image.
    Additionally prints 'fork detected' if class 42 ('fork') is found.
    If the top of the human bounding box is in the bottom half of the image, 'slam' is set to True.
    """

    # Decode Base64 -> NumPy Array
    decoded_bytes = base64.b64decode(base64_image)
    img_array = np.frombuffer(decoded_bytes, np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    # Inference
    results = model(frame)

    # Convert to NumPy
    data = results.xyxy[0].cpu().numpy()

    # Filter detections for humans (class 0 = 'person' for YOLOv5)
    person_detections = data[data[:, 5] == 0]
    if len(person_detections) == 0:
        return "middle"  # default fallback if no human is detected

    # Take the first detected person (assuming only one)
    x_min, y_min, x_max, y_max, conf, cls = person_detections[0]
    width = frame.shape[1]
    height = frame.shape[0]
    center_x = (x_min + x_max) / 2.0

    direction = ""
    rotate = False
    slam = False

    # Determine direction
    if center_x < width / 3.0:
        direction = "left"
    elif center_x > 2.0 * width / 3.0:
        direction = "right"
    else:
        direction = "middle"

    # If the top of the bounding box is in the bottom half of the frame, slam = True
    if y_min > height / 2.0:
        slam = True

    # Check for forks (class 42 in YOLO)
    fork_detections = data[data[:, 5] == 42]
    if len(fork_detections) > 0:
        rotate = True

    send_control_signal(direction, rotate, slam)


def send_control_signal(direction: str, rotate: bool, slam: bool):
    # Create the data dictionary
    data = {"direction": direction, "rotate": rotate, "slam": slam}

    # Send the POST request with the data as JSON
    response = requests.post(
        "http://127.0.0.1:5000/control", json=data  # Specify the data as JSON
    )

    # check the response
    if response.status_code != 200:
        print(f"Failed to send control signal: {response.status_code}, {response.text}")


def send_start_game():
    requests.get("http://127.0.0.1:5000/start")


def send_restart_game():
    requests.get("http://127.0.0.1:5000/restart")


def request_inference_threaded(base64_image: str, model) -> None:
    threading.Thread(
        target=request_inference,
        args=(
            base64_image,
            model,
        ),
    ).start()

def start_game_threaded() -> None:
    threading.Thread(target=send_start_game).start()