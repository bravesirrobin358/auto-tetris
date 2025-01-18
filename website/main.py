import streamlit as st
import base64
import cv2


client: Groq = Groq(api_key=api_key)

def request_inference(img: np.ndarray) -> None:
    """
    Sends an image for inference, using Groq's API and prints the result.
    """
    base64_image: str = encode_frame(img)
    chat_completion: Any = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        model="llama-3.2-11b-vision-preview",
    )
    print(chat_completion.choices[0].message.content)

def main():
    st.set_page_config(page_title="Streamlit WebCam App")
    st.title("Webcam Display Steamlit App")
    st.caption("Powered by OpenCV, Streamlit")
    cap = cv2.VideoCapture(1)
    frame_placeholder = st.empty()
    stop_button_pressed = st.button("Stop")
    while cap.isOpened() and not stop_button_pressed:
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break
        frame_bytes = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB).tobytes()
        frame_base64_str = base64.encodebytes(frame).decode()
        frame_placeholder.image(frame,channels="RGB")
        if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
