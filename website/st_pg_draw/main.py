import streamlit as st
from streamlit_ace import st_ace, THEMES
import pygame
import pygame.gfxdraw
from PIL import Image
import numpy
import numpy as np

from safe_builtins import safe_builtins, validate_code
from examples import examples


st.set_page_config(
    layout="wide",
    page_title="Pygame-CE Drawing Sandbox",
    page_icon="🎨",
)

css_page_style = '''
<style>
section.main > div:has(~ footer ) {
    padding-top: 10px;
    padding-bottom: 0px;
    padding-left: 25px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
'''
st.markdown(css_page_style, unsafe_allow_html=True)

st.title("Pygame-CE Drawing Sandbox 🎨:snake:")
st.write("Experiment and test out Pygame (Community Edition) static drawing functions with a real-time preview.")
st.markdown("In this sandboxed environment, `pygame`, `pygame.gfxdraw`, and `numpy` are imported and a limited set of Python `builtins` are available for use.")
st.markdown("The display surface variable is named `SCREEN`, it's size is `(800, 600)` and is accessible via `SCREEN_SIZE`, and uploaded image surface accessible via `IMAGE_SURFACE`.")
st.markdown("Feel free to tag or message me on the [Pygame-CE Discord](https://discord.com/channels/772505616680878080/772505616680878083) `@Djo` for any questions or suggestions. The source code for this Streamlit app is available on GitHub by following the icon link at the top right of the page.")

with st.form('Editor Settings'):
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        example_names = list(examples.keys())
        example = st.selectbox('Load Example', example_names, index=example_names.index("Default"))
    with col2:
        st.selectbox('Editor Theme', THEMES, index=THEMES.index('gruvbox'), key="editor_theme")
        st.checkbox('Wrap Editor Text', value=True, key="wrap")
    with col3:
        st.slider('Editor Font Size', 14, 50, 24, 1, key="font_size")
    with col4:
        st.slider("Editor Height", 200, 1000, 600, 50, key="editor_height")
    with col5:
        st.file_uploader("Upload Image File (access via `IMAGE_SURFACE`)", type=["png", "jpeg"], key="image_file")

    submitted = st.form_submit_button('Apply (RESETS editor content)')

status = st.container()
col1, col2 = st.columns(2)

with col1:
    st.session_state["code"] = st_ace(
        value=examples[example],
        language="python",
        theme=st.session_state["editor_theme"],
        font_size=st.session_state["font_size"],
        height=st.session_state["editor_height"],
        wrap=st.session_state["wrap"],
        auto_update=True,
    )

pygame.init()
pygame.font.init()

SCREEN_SIZE = (800, 600)
SCREEN = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
SCREEN.fill((0, 0, 0))

if "image_file" in st.session_state:
    if st.session_state["image_file"]:
        img_opened = Image.open(st.session_state["image_file"])
        img_size = img_opened.size
        IMAGE_SURFACE = pygame.image.frombytes(img_opened.tobytes(), img_size, img_opened.mode)
    else:
        IMAGE_SURFACE = None

try:
    validate_code(st.session_state["code"])
    limited_globals = {
        '__builtins__': safe_builtins, 
        'pygame': pygame, 
        'pygame.gfxdraw': pygame.gfxdraw, 
        'np': np, 
        'numpy': numpy, 
        'SCREEN': SCREEN, 
        'SCREEN_SIZE': SCREEN_SIZE,
        'IMAGE_SURFACE': IMAGE_SURFACE if "image_file" in st.session_state else None,
    }
    exec(st.session_state["code"], limited_globals)
    status.success('Code executed successfully')
except Exception as e:
    status.error(f"{type(e).__name__}: {e}")

with col2:
    img = Image.frombytes('RGB', SCREEN_SIZE, pygame.image.tobytes(SCREEN, 'RGB'))
    st.image(img)
