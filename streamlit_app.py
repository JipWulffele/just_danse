import streamlit as st
import cv2
from core.dance_session import DanceSession
from utils.utils_streamlit import load_icons

# ---------- Dances config
DANCES = {
    "Unicorn Dance": {
        "ref_video": "assets/video/reference_unicorn.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_unicorn.npz",
        "audio": "assets/audio/de_kabouter_dans_short.mp3",
        "icon_path": "assets/config/icon_schedule.json",
        "webcam_rotation": 90,
    },
}

STICKER = {"last_sticker_duration": 0,
           "sticker_start_time": 0,
           "sticker_interval": 3.0,
           "sticker_duration": 1.5,
           "current_sticker_score": 0,
           "last_sticker_time": 0}

ICON_PATH = "assets/config/icon_schedule.json"
icon_data = load_icons(ICON_PATH)

# ---------- Sidebar
st.sidebar.title("Lets dance!")
dance_choice = st.sidebar.selectbox("Choose your dance:", list(DANCES.keys()))
difficulty = st.sidebar.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])
start_button = st.sidebar.checkbox('Run')

# ---------- Main panel
st.title("💃 Dance 🕺")
FRAME_WINDOW = st.image([])
dance_session = DanceSession(DANCES[dance_choice], STICKER)

while start_button:
    dance_session = DanceSession(DANCES[dance_choice],
                                STICKER, icon_data=icon_data,
                                frame_window=FRAME_WINDOW)

    detected, frame = dance_session.wait_for_person_and_countdown()

    if detected:
        st.write("🎉 Person detected! Starting dance!")
        dance_session.dance_loop()
        start_button = False

st.write('Stopped')
dance_session.release()
