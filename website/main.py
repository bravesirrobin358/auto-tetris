import streamlit as st
import cv2
import base64
import threading
import torch
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(page_title="Streamlit Tetris App")

RATE_LIMITER = 10


# Load the YOLO model once (e.g., YOLOv5s)
@st.cache_resource
def get_pretrained_model():
    # Create a database session object that points to the URL.
    return torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)


model = get_pretrained_model()


def request_inference(base64_image: str) -> str:
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


def request_inference_threaded(base64_image: str) -> None:
    threading.Thread(target=request_inference, args=(base64_image,)).start()


def main():
    st.title("Webcam Display Steamlit App")
    st.caption("Powered by OpenCV, Streamlit")

    cap = cv2.VideoCapture(1)
    frame_placeholder = st.empty()
    stop_button_pressed = st.button("Stop")

    frame_count = 0

    while cap.isOpened() and not stop_button_pressed:
        frame_count += 1
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        success, encoded_image = cv2.imencode(".jpg", frame)
        if success and frame_count == RATE_LIMITER:
            frame_count = 0
            frame_base64_str = base64.b64encode(encoded_image).decode("utf-8")
            # Use the threaded inference call
            position = request_inference_threaded(frame_base64_str)


        frame_placeholder.image(frame, channels="RGB")

        if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
