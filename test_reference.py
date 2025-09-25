import time
import cv2
import streamlit as st

from core.video_handler import VideoHandler

st.title("Reference Video Player")

REF_VIDEO = "assets/video/reference_unicorn.webm"
FRAME_WINDOW = st.image([])

run = st.checkbox("Run Reference Video")

if run:
    ref = VideoHandler(source=REF_VIDEO)
    ref.set_rotation(-90)
    ref.set_target_size(width=640, height=480)

    while run:
        frame = ref.get_frame()
        if frame is None:
            st.write("Video ended")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        FRAME_WINDOW.image(frame_rgb)
        time.sleep(0.04)  # ~25 FPS

    ref.release()
else:
    st.write("Stopped")
