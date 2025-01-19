import streamlit as st
import cv2
import base64
import torch
import warnings
from PIL import Image
import requests
from helpers import (
    request_inference_threaded,
    start_game_threaded,
    send_restart_game,
)

warnings.filterwarnings("ignore", category=FutureWarning)

st.set_page_config(
    page_title="Streamlit Tetris App", layout="wide", page_icon=":video_game:"
)

with st.sidebar:
    st.write("**Sweatris Controls**")
    
    st.write("- Move left and right in the camera frame to move the falling piece.")
    st.write("- Crouch to slam the piece downwards.")
    st.write("- Click to rotate.")
    
    if not st.session_state.get("playing", False):
        start_game = st.button("Start Game")
        
        if start_game:
            st.session_state.playing = True
            start_game_threaded()
            st.rerun()
            
    else:
        restart_button = st.button("Restart Game")
        if restart_button:
            send_restart_game()
        
        
    

RATE_LIMITER = 15


@st.cache_resource
def get_pretrained_model():
    return torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)


model = get_pretrained_model()


def main():
    st.markdown(
        "<h1 style='text-align: center;'>Sweatris</h1>",
        unsafe_allow_html=True,
    )
    
    st.markdown(
        "<p style='text-align: center; font-size: 18px;'>Welcome to Sweatris, an AI powered Tetris Game to get you moving!</p>",
        unsafe_allow_html=True,
    )

    if "playing" not in st.session_state:
        st.session_state.playing = False

    if st.session_state.playing:
        playing()


def playing():

    restart_button = st.button("Restart Game")
    if restart_button:
        send_restart_game()


    # Define columns once, outside any loop
    col1, col2 = st.columns(2, vertical_alignment="center")

    # Set vertical alignment to center
    col1.subheader("Webcam")
    col1.empty()

    col2.subheader("Game")
    col2.empty()

    # Placeholders for each column
    webcam_placeholder = col1.empty()
    game_placeholder = col2.empty()

    cap = cv2.VideoCapture(0)

    frame_count = 0
    
    st.audio("song.mp3", loop=True, autoplay=True)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break
        frame = cv2.flip(frame, 1)
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
