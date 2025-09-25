import time
import cv2
import streamlit as st
from core.video_handler import VideoHandler

# Constants
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
VIDEO_PATH = "assets/video/reference_unicorn.webm"

# Initialize video handler
video = VideoHandler(source=VIDEO_PATH)
video.set_target_size(width=FRAME_WIDTH, height=FRAME_HEIGHT)

# Create a placeholder for the video frame
frame_placeholder = st.empty()

# Start button
if st.button("Start"):
    # Start video playback
    while True:
        frame = video.get_frame()
        if frame is None:
            st.write("Video finished")
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_placeholder.image(frame_rgb)
        time.sleep(0.04)  # ~25 FPS
