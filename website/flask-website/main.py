import streamlit as st
from PIL import Image
import base64
import requests

st.set_page_config(
        layout="wide",
        page_title="Pygame-CE Drawing Sandbox",
        page_icon="🎨",
)

# st.empty() makes it so st.image() gets replaced by the next image from the api
with st.empty():
    while True:
        response = requests.get("http://127.0.0.1:5000").json()["b64frame"]
        if response != None:
            st.image(Image.frombytes(mode="RGB",size=(400, 500), data=base64.b64decode(response)))