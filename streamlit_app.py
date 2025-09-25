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
        "webcam_rotation": -90,
    },
    "Old Dance": {
        "ref_video": "assets/video/reference.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference1.npz",
        "audio": "assets/audio/de_kabouter_dans_ultra_short_2.mp3",
        "icon_path": "assets/config/icon_schedule_old.json",
        "webcam_rotation": 90,
    },
    "Dabca": {
        "ref_video": "assets/video/dabca.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference1.npz",
        "audio": "assets/audio/dabca_music.mp3",
        "icon_path": "assets/config/icon_schedule_old.json",
        "webcam_rotation": -90,
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

# Initialize state variables
if "dance_running" not in st.session_state:
    st.session_state.dance_running = False

# ---------- Sidebar
st.sidebar.title("Lets dance!")
dance_choice = st.sidebar.selectbox("Choose your dance:", list(DANCES.keys()))
difficulty = st.sidebar.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])

start_button = st.sidebar.button("Start Dance")

# ---------- Main panel
st.title("💃 Lets dance 🕺")
FRAME_WINDOW = st.image([])

if start_button:
    st.session_state.dance_running = True

if st.session_state.dance_running:
    dance_session = DanceSession(DANCES[dance_choice],
                                  STICKER, icon_data=icon_data,
                                  frame_window=FRAME_WINDOW)

    detected, frame = dance_session.wait_for_person_and_countdown()

    if detected:
        dance_session.dance_loop()

    dance_session.release()
    st.session_state.dance_running = False  # re-enable button at the end