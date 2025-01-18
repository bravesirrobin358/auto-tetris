import streamlit as st
import cv2
import base64
import threading
from groq import Groq
from api_key import API_KEY

RATE_LIMITER = 50

# Global variables to be updated asynchronously
left_right_position = None
hands_above_head = None
arms_outside = None

client: Groq = Groq(api_key=API_KEY)


def set_controls(parsed_response: str):
    global left_right_position, hands_above_head, arms_outside
    lines = parsed_response.split("\n")
    for line in lines:
        parsed_line = line[3:].strip(" ()").lower()
        if line.startswith("1."):
            # Expected format: 1. (left, right, middle)
            if parsed_line in ["left, right, middle"]:
                left_right_position = parsed_line
        elif line.startswith("2."):
            # Expected format: 2. (yes, no)
            if parsed_line in ["yes", "no"]:
                hands_above_head = line[3:].strip(" ()")
        elif line.startswith("3."):
            # Expected format: 3. (yes, no)
            if parsed_line in ["yes", "no"]:
                arms_outside = line[3:].strip(" ()")


def parse_response(response: str) -> str:
    lines = response.splitlines()
    # Remove trailing whitespace from each line
    lines = [line.rstrip().lower() for line in lines]
    # Keep only lines that start with '1', '2', or '3'
    lines = [line for line in lines if line.startswith(("1", "2", "3"))]
    return "\n".join(lines)


def request_inference(base64_image: str) -> None:
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": """1. Is the person in the image standing on the left, right, or middle?
2. Does the person in the image have both hands above their head?
3. Does the person in the image have both arms straight out to their sides (in a T pose)?

Reply in the following format. NO OTHER FORMAT IS ACCEPTABLE!!! If you respond with anything other than the options below the program will fail.

1. (left, right, middle)
2. (yes, no)
3. (yes, no)

2 and 3 are mutually exclusive

If there is no person, or the person is not fully visible in the image (from at least the hips up) respond "None"

""",
                    },
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
    parsed_response = parse_response(chat_completion.choices[0].message.content)
    print(parsed_response)
    print()
    set_controls(parsed_response)


def request_inference_threaded(base64_image: str) -> None:
    threading.Thread(target=request_inference, args=(base64_image,)).start()


def main():
    st.set_page_config(page_title="Streamlit WebCam App")
    st.title("Webcam Display Steamlit App")
    st.caption("Powered by OpenCV, Streamlit")

    cap = cv2.VideoCapture(0)
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
            request_inference_threaded(frame_base64_str)

        frame_placeholder.image(frame, channels="RGB")

        if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
