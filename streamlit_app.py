import streamlit as st
import cv2
from core.dance_session import DanceSession

# ---------- Dances config
DANCES = {
    "Unicorn Dance": {
        "ref_video": "assets/video/reference_unicorn.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_unicorn.npz",
        "audio": "assets/audio/de_kabouter_dans_short.mp3",
        "icon_path": "assets/config/icon_schedule.json",
    },
}

# ---------- Sidebar
st.sidebar.title("Lets dance!")
dance_choice = st.sidebar.selectbox("Choose your dance:", list(DANCES.keys()))
difficulty = st.sidebar.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])
start_button = st.sidebar.checkbox('Run')

# ---------- Main panel
st.title("💃 Dance 🕺")
FRAME_WINDOW = st.image([])

dance_session = DanceSession(DANCES[dance_choice])

while start_button:
    dance_session = DanceSession(DANCES[dance_choice], frame_window=FRAME_WINDOW)

    detected, frame = dance_session.wait_for_person_and_countdown()

    if detected:
        st.write("🎉 Person detected! Starting dance!")
        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

st.write('Stopped')
dance_session.release()
