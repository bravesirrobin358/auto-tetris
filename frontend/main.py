import streamlit as st
import cv2
import base64
import torch
import warnings
from PIL import Image
import requests
from helpers import (
    request_inference_threaded,
    send_start_game,
    send_restart_game,
    send_click_event,
)

warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(
    page_title="Streamlit Tetris App", layout="wide", page_icon=":video_game:"
)

RATE_LIMITER = 15


@st.cache_resource
def get_pretrained_model():
    return torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)


model = get_pretrained_model()


def main():
    st.title("Tetris Fitness Game :weight_lifter:")

    if "playing" not in st.session_state:
        st.session_state.playing = False

    if st.session_state.playing:
        playing()
    else:
        start_menu()


def start_menu():
    st.write("Welcome to Sweatris, an AI powered Tetris Game to get you moving!")
    start_game = st.button("Start Game")

    if start_game:
        st.session_state.playing = True
        send_start_game()
        st.rerun()


def playing():

    restart_button = st.button("Restart Game")

    if restart_button:
        send_restart_game()

    rotate_button = st.button("Rotate")

    if rotate_button:
        send_click_event()

    # Define columns once, outside any loop
    col1, col2 = st.columns(2)

    # Placeholders for each column
    webcam_placeholder = col1.empty()
    game_placeholder = col2.empty()

    cap = cv2.VideoCapture(0)

    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        success, encoded_image = cv2.imencode(".jpg", frame)

        # Rate limit for inference
        frame_count += 1
        if success and frame_count >= RATE_LIMITER:
            frame_count = 0
            frame_base64_str = base64.b64encode(encoded_image).decode("utf-8")
            request_inference_threaded(frame_base64_str, model)

        # Update the left column placeholder
        webcam_placeholder.image(frame, channels="RGB")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

        # Update the right column placeholder
        response = requests.get("http://127.0.0.1:5000").json().get("b64frame")
        if response:
            decoded = base64.b64decode(response)
            frame_img = Image.frombytes("RGB", (400, 500), decoded)
            game_placeholder.image(frame_img)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
