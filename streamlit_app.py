import streamlit as st
import cv2
from core.dance_session import DanceSession
from utils.utils_streamlit import load_icons
from core.ecran import Ecran

# ---------- Dances config
DANCES = {
    "Unicorn Dance": {
        "ref_video": "assets/video/reference_unicorn.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_unicorn.npz",
        "audio": "assets/audio/de_kabouter_dans_short.mp3",
        "icon_path": "assets/config/icon_schedule.json",
        "webcam_rotation": -90,
        "FPS": 30,
    },
    "Not unicorn dance": {
        "ref_video": "assets/video/reference.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference1.npz",
        "audio": "assets/audio/de_kabouter_dans_ultra_short_2.mp3",
        "icon_path": "assets/config/icon_schedule_old.json",
        "webcam_rotation": 90,
        "FPS": 25,
    },
    "Dabke (1 pers.)": {
        "ref_video": "assets/video/dabca.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_dabca.npz",
        "audio": "assets/audio/dabca_music.mp3",
        "icon_path": "assets/config/icon_schedule_dabke_1p.json",
        "webcam_rotation": -90,
        "FPS": 30,
    },
    "Dabke (2 pers.)": {
        "ref_video": "assets/video/dabke_2p_crop.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_dabca.npz",
        "audio": "assets/audio/dabke_music_crop.mp3",
        "icon_path": "assets/config/icon_schedule_dabke_2p.json",
        "webcam_rotation": 0,
        "FPS": 20,
    },
    "Italian dance (1 pers.)": {
        "ref_video": "assets/video/italian_1p_crop.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_dabca.npz",
        "audio": "assets/audio/italian_music_crop.mp3",
        "icon_path": "assets/config/icon_schedule_italian_1p.json",
        "webcam_rotation": 0,
        "FPS": 20,
    },
    "Italian dance (2 pers.)": {
        "ref_video": "assets/video/italian_crop.webm",
        "ref_keypoints": "assets/keypoints/keypoints_reference_dabca.npz",
        "audio": "assets/audio/italian_music_crop.mp3",
        "icon_path": "assets/config/icon_schedule_italian_2p.json",
        "webcam_rotation": 0,
        "FPS": 20,
    },
}

STICKER = {"last_sticker_duration": 0,
           "sticker_start_time": 0,
           "sticker_interval": 3.0,
           "sticker_duration": 1.5,
           "current_sticker_score": 0,
           "last_sticker_time": 0}

SOURCE = 0

# Initialize state variables
if "dance_running" not in st.session_state:
    st.session_state.dance_running = False

# ---------- Sidebar
st.sidebar.title("Lets dance!")
dance_choice = st.sidebar.selectbox("Choose your dance:", list(DANCES.keys()))
difficulty = st.sidebar.selectbox("Difficulty:", ["Easy", "Medium", "Hard"])
fall_detection = st.sidebar.selectbox("Fall detection:", ["Off", "On"])

start_button = st.sidebar.button("Start Dance")

# ---------- Main panel
FRAME_WINDOW = st.image([])

# ecran de depart
ecran = Ecran() # Start screen
start_screen_frame = ecran.get_ecran_start(size=(1080, 720))
FRAME_WINDOW.image(cv2.cvtColor(start_screen_frame , cv2.COLOR_BGR2RGB))

if start_button:
    st.session_state.dance_running = True


if st.session_state.dance_running:
    dance_session = DanceSession(DANCES[dance_choice],
                                 STICKER, 
                                 source=SOURCE,
                                 frame_window=FRAME_WINDOW,
                                 difficulty_levels=difficulty,
                                 fall_detection=fall_detection)
    dance_session.audio_player.stop()

    detected, frame = dance_session.wait_for_person_and_countdown()

    if detected:
        dance_session.dance_loop()

    dance_session.release()
    st.session_state.dance_running = False  # re-enable button at the end