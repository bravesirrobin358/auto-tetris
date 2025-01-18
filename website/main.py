import streamlit as st
import cv2
import base64
from groq import Groq
from api_key import API_KEY

client: Groq = Groq(api_key=API_KEY)


def request_inference(base64_image: str) -> None:
    chat_completion = client.chat.completions.create(
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

    cap = cv2.VideoCapture(0)
    frame_placeholder = st.empty()
    stop_button_pressed = st.button("Stop")

    while cap.isOpened() and not stop_button_pressed:
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Encode the frame as JPEG in memory
        success, encoded_image = cv2.imencode(".jpg", frame)
        if success:
            # Convert the encoded bytes to base64
            frame_base64_str = base64.b64encode(encoded_image).decode("utf-8")
            request_inference(frame_base64_str)

        frame_placeholder.image(frame, channels="RGB")

        if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
