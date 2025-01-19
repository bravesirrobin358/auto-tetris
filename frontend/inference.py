import threading
import base64
import cv2
import numpy as np


def request_inference(base64_image: str, model) -> str:
    """
    Uses a YOLO model to detect a person in the image and returns 'left', 'right', or 'middle'
    based on the person's center relative to the image width. Assumes one human in the image.
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
    center_x = (x_min + x_max) / 2.0

    # Determine position
    if center_x < width / 3.0:
        print("left")
        return "left"
    elif center_x > 2.0 * width / 3.0:
        print("right")
        return "right"
    else:
        print("middle")
        return "middle"


def request_inference_threaded(base64_image: str, model) -> None:
    threading.Thread(target=request_inference, args=(base64_image, model,)).start()
