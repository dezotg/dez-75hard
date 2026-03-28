import streamlit as st
import json
import os
import calendar
import random
import base64
import hmac
from html import escape
from datetime import date, datetime, timedelta
from typing import Dict, Any

import pandas as pd

st.set_page_config(
    page_title="Dez 75 Hard Command Center",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_FILE = "seventyfive_data.json"
IMG_DIR = "images"

HERO_IMG = os.path.join(IMG_DIR, "hero.jpg")
WORKOUT_IMG = os.path.join(IMG_DIR, "workout.jpg")
PROGRESS_IMG = os.path.join(IMG_DIR, "progress.jpg")
COMMUNITY_IMG = os.path.join(IMG_DIR, "community.jpg")
COACH_IMG = os.path.join(IMG_DIR, "coach.jpg")
MISSION_NATURE_IMG = "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1400&q=80"


# =========================================================
# IMAGE HELPERS
# =========================================================
def image_to_data_uri(path: str) -> str:
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    if ext == "jpg":
        ext = "jpeg"
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{ext};base64,{encoded}"


def background_style(image_path: str, overlay: str, size: str = "cover", position: str = "center 28%") -> str:
    if image_path.startswith("http://") or image_path.startswith("https://"):
        return f"background: {overlay}, url('{image_path}'); background-size: {size}; background-position: {position}; background-repeat: no-repeat;"

    uri = image_to_data_uri(image_path)
    if uri:
        return f"background: {overlay}, url('{uri}'); background-size: {size}; background-position: {position}; background-repeat: no-repeat;"
    return f"background: {overlay};"


# =========================================================
# STYLES
# =========================================================
def inject_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Archivo+Expanded:wght@600;700;800;900&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root {
        --bg: #0b0e14;
        --bg2: #171c26;
        --panel: rgba(20, 25, 36, 0.82);
        --panel2: rgba(29, 36, 50, 0.88);
        --text: #f8fafc;
        --muted: #d2dceb;
        --soft: #94a3b8;
        --red: #991b1b;
        --red2: #dc2626;
        --red3: #fb7185;
        --line: rgba(255,255,255,0.08);
    }

    html, body, [class*="css"], [data-testid="stAppViewContainer"] * {
        font-family: "Manrope", "Segoe UI", sans-serif;
    }

    /* Keep Streamlit/Material icon ligatures from rendering as plain text. */
    .material-icons,
    .material-icons-round,
    .material-icons-outlined,
    .material-symbols-rounded,
    .material-symbols-outlined,
    [class*="material-symbols"],
    [data-testid="stSidebar"] button span[aria-hidden="true"] {
        font-family: "Material Symbols Rounded", "Material Symbols Outlined", "Material Icons" !important;
        font-weight: normal !important;
        font-style: normal !important;
        letter-spacing: normal !important;
        text-transform: none !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 10%, rgba(220,38,38,0.16), transparent 26%),
            radial-gradient(circle at 88% 8%, rgba(251,113,133,0.12), transparent 24%),
            radial-gradient(circle at 50% 100%, rgba(251,191,36,0.08), transparent 28%),
            linear-gradient(180deg, #0a0d13 0%, #121722 44%, #1a2130 100%);
        color: var(--text) !important;
    }

    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 300px;
        width: 72px;
        height: 100vh;
        pointer-events: none;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.00) 20%, rgba(255,255,255,0.00) 80%, rgba(255,255,255,0.04)),
            linear-gradient(180deg, rgba(153,27,27,0.18), rgba(10,13,19,0.00) 30%, rgba(10,13,19,0.00) 70%, rgba(59,130,246,0.10)),
            repeating-linear-gradient(180deg, rgba(255,255,255,0.04) 0 1px, transparent 1px 16px);
        border-left: 1px solid rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.03);
        opacity: 0.42;
        z-index: 0;
    }

    .block-container {
        max-width: 1480px;
        padding-top: 1.15rem;
        padding-bottom: 2.5rem;
        position: relative;
        z-index: 1;
    }

    header[data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarHeader"],
    section[data-testid="stSidebar"] > div:first-child > div:first-child > button,
    section[data-testid="stSidebar"] button[kind="header"],
    section[data-testid="stSidebar"] [aria-label*="sidebar"],
    section[data-testid="stSidebar"] [title*="sidebar"] {
        display: none !important;
    }

    .stApp {
        margin-top: 0 !important;
    }

    h1, h2, h3, h4, h5, h6, p, div, span, label, li {
        color: var(--text) !important;
    }

    h1, h2, h3, h4, h5, h6,
    .hero-title,
    .feature-title,
    .section-title,
    .stat-value,
    .brand-left {
        font-family: "Archivo Expanded", "Arial Black", sans-serif !important;
    }

    [data-testid="stSidebar"] {
        background:
            radial-gradient(circle at top, rgba(220,38,38,0.14), transparent 34%),
            linear-gradient(180deg, #121723 0%, #1b2230 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.08) !important;
        min-width: 300px !important;
        width: 300px !important;
    }

    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 300px !important;
        width: 300px !important;
        margin-left: 0 !important;
        transform: none !important;
    }

    [data-testid="stSidebar"] * {
        color: #ffffff !important;
    }

    .stTextInput input,
    .stNumberInput input,
    .stDateInput input,
    .stTextArea textarea,
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stDateInput > div > div input,
    .stTextArea textarea,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stDateInput input,
    [data-testid="stSidebar"] .stTextArea textarea {
        background: rgba(5, 10, 19, 0.96) !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        caret-color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 14px !important;
        box-shadow: inset 0 1px 0 rgba(255,255,255,0.04) !important;
    }

    .stTextInput input::placeholder,
    .stNumberInput input::placeholder,
    .stDateInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
        -webkit-text-fill-color: #94a3b8 !important;
        opacity: 1 !important;
    }

    .stSelectbox div[data-baseweb="select"] > div,
    .stMultiSelect div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(5, 10, 19, 0.96) !important;
        color: #ffffff !important;
        border: 1px solid #334155 !important;
        border-radius: 14px !important;
    }

    .stCheckbox label {
        color: #ffffff !important;
    }

    details[data-testid="stExpander"] {
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        background: rgba(255,255,255,0.03) !important;
        overflow: hidden;
    }

    details[data-testid="stExpander"] summary {
        padding: 0.9rem 1rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
    }

    details[data-testid="stExpander"] summary:hover {
        background: rgba(255,255,255,0.03) !important;
    }

    details[data-testid="stExpander"] summary svg {
        fill: #fca5a5 !important;
    }

    [data-testid="stTabs"] {
        margin-top: 0.75rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06);
        padding: 0.45rem;
        border-radius: 22px;
        margin-bottom: 1.15rem;
        overflow-x: auto;
    }

    button[data-baseweb="tab"] {
        color: #dbe3ef !important;
        font-weight: 800 !important;
        border-radius: 16px !important;
        padding: 0.75rem 1rem !important;
        background: transparent !important;
        border: 1px solid transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #ffffff !important;
        background: linear-gradient(135deg, rgba(153,27,27,0.95), rgba(220,38,38,0.95)) !important;
        border-color: rgba(255,255,255,0.09) !important;
        box-shadow: 0 10px 24px rgba(153,27,27,0.28) !important;
    }

    .stButton > button,
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--red), var(--red2)) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        min-height: 2.9rem !important;
        box-shadow: 0 12px 28px rgba(185,28,28,0.24) !important;
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #dc2626 0%, #fb7185 100%) !important;
    }

    .stProgress > div {
        background: rgba(255,255,255,0.07) !important;
        border-radius: 999px !important;
    }

    .top-brand {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1rem;
    }

    .brand-left {
        font-size: 1.35rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        color: #ffffff !important;
    }

    .brand-right {
        color: #fca5a5 !important;
        font-size: 0.9rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.14em;
    }

    .hero {
        position: relative;
        overflow: hidden;
        border-radius: 32px;
        min-height: 490px;
        padding: 2.7rem 2.7rem 2.2rem 2.7rem;
        border: 1px solid rgba(255,255,255,0.10);
        box-shadow: 0 28px 70px rgba(0,0,0,0.34);
        margin-bottom: 1.1rem;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }

    .hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(180deg, rgba(0,0,0,0.10), rgba(0,0,0,0.55)),
            linear-gradient(120deg, rgba(255,255,255,0.10), transparent 32%);
        pointer-events: none;
    }

    .hero > * {
        position: relative;
        z-index: 1;
    }

    .hero-eyebrow {
        color: #fecaca !important;
        font-size: 0.82rem;
        font-weight: 900;
        text-transform: uppercase;
        letter-spacing: 0.18em;
        margin-bottom: 0.6rem;
    }

    .hero-title {
        font-size: 4.3rem;
        line-height: 0.9;
        font-weight: 900;
        letter-spacing: -0.05em;
        margin-bottom: 0.9rem;
        color: #ffffff !important;
        max-width: 820px;
    }

    .hero-sub {
        color: #e7edf8 !important;
        font-size: 1.08rem;
        max-width: 720px;
        margin-bottom: 1.2rem;
    }

    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }

    .pill {
        display: inline-block;
        padding: 0.58rem 0.88rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.10);
        border: 1px solid rgba(255,255,255,0.12);
        color: #ffffff !important;
        font-size: 0.84rem;
        font-weight: 800;
        backdrop-filter: blur(8px);
    }

    .glass-card {
        border-radius: 26px;
        background: linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.08);
        padding: 1.1rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 18px 42px rgba(0,0,0,0.20);
        backdrop-filter: blur(10px);
    }

    .section-kicker {
        color: #fca5a5 !important;
        text-transform: uppercase;
        letter-spacing: 0.16em;
        font-size: 0.78rem;
        font-weight: 900;
        margin-bottom: 0.45rem;
    }

    .section-title {
        color: #ffffff !important;
        font-size: 1.42rem;
        font-weight: 900;
        letter-spacing: -0.02em;
        margin-bottom: 0.35rem;
    }

    .section-sub {
        color: #cbd5e1 !important;
        font-size: 0.96rem;
    }

    .stat-card {
        border-radius: 24px;
        padding: 1.2rem 1.05rem 1rem 1.05rem;
        min-height: 145px;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.12), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 18px 40px rgba(0,0,0,0.18);
    }

    .stat-label {
        color: #c9d5e6 !important;
        font-size: 0.92rem;
        margin-bottom: 0.3rem;
    }

    .stat-value {
        color: #ffffff !important;
        font-size: 2.25rem;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -0.04em;
    }

    .stat-sub {
        color: #dce7f5 !important;
        font-size: 0.92rem;
        margin-top: 0.35rem;
    }

    .feature-banner {
        position: relative;
        overflow: hidden;
        border-radius: 28px;
        min-height: 360px;
        padding: 1.5rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 18px 48px rgba(0,0,0,0.24);
        display: flex;
        flex-direction: column;
        margin-bottom: 1rem;
    }

    .feature-banner::before {
        content: "";
        position: absolute;
        inset: 0;
        background:
            linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.10)),
            linear-gradient(90deg, rgba(5,7,11,0.28) 0%, rgba(5,7,11,0.10) 24%, rgba(5,7,11,0.00) 52%);
        pointer-events: none;
    }

    .feature-banner > * {
        position: relative;
        z-index: 1;
    }

    .feature-copy {
        position: absolute;
        left: 56%;
        top: 0.35rem;
        transform: translateX(-50%);
        width: min(320px, 40%);
        padding: 0.72rem 0.8rem;
        border-radius: 16px;
        background: linear-gradient(180deg, rgba(7,10,16,0.56), rgba(18,24,35,0.30));
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow: 0 10px 22px rgba(0,0,0,0.14);
        backdrop-filter: blur(6px);
    }

    .feature-copy.bottom-left {
        left: 0.7rem;
        top: auto;
        bottom: 0.7rem;
        transform: none;
    }

    .feature-banner.red-block {
        background: linear-gradient(135deg, #991b1b, #ef4444) !important;
        color: #ffffff !important;
    }

    .feature-title {
        font-size: 1.28rem;
        line-height: 1.0;
        font-weight: 900;
        letter-spacing: -0.04em;
        margin-bottom: 0.32rem;
    }

    .feature-text {
        font-size: 0.8rem;
        color: #edf2f8 !important;
        max-width: 300px;
    }

    .mini-banner {
        border-radius: 22px;
        min-height: 190px;
        padding: 1.2rem;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 14px 34px rgba(0,0,0,0.20);
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
        margin-bottom: 1rem;
        overflow: hidden;
    }

    .coach-user {
        background: rgba(185,28,28,.18);
        border: 1px solid rgba(239,68,68,.34);
        padding: 14px;
        border-radius: 16px;
        margin-bottom: 8px;
    }

    .coach-ai {
        background: rgba(255,255,255,.05);
        border: 1px solid rgba(255,255,255,.10);
        padding: 14px;
        border-radius: 16px;
        margin-bottom: 8px;
    }

    .small-muted {
        color: #cbd5e1 !important;
        font-size: 0.88rem;
    }

    .calendar-box {
        border-radius: 16px;
        min-height: 92px;
        padding: 0.6rem;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.06);
    }

    .calendar-empty {
        border-radius: 16px;
        min-height: 92px;
        background: rgba(255,255,255,0.02);
        border: 1px dashed rgba(255,255,255,0.04);
    }

    .calendar-head {
        text-align: center;
        font-size: 0.83rem;
        color: #cbd5e1 !important;
        font-weight: 900;
        margin-bottom: 0.2rem;
    }

    .footer-note {
        color: #b8c7da !important;
        text-align: center;
        font-size: 0.84rem;
        margin-top: 1.3rem;
    }

    .status-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.8rem;
        margin-top: 0.85rem;
        margin-bottom: 0.9rem;
    }

    .status-item {
        padding: 0.9rem 0.95rem;
        border-radius: 18px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
    }

    .status-item.done {
        background: linear-gradient(180deg, rgba(22,163,74,0.18), rgba(34,197,94,0.08));
        border-color: rgba(74,222,128,0.18);
    }

    .status-item.open {
        background: linear-gradient(180deg, rgba(220,38,38,0.16), rgba(255,255,255,0.03));
        border-color: rgba(248,113,113,0.16);
    }

    .status-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #d7e1ef !important;
        margin-bottom: 0.35rem;
        font-weight: 800;
    }

    .status-value {
        font-size: 1rem;
        font-weight: 800;
        line-height: 1.3;
    }

    .list-card {
        border-radius: 22px;
        padding: 1rem 1.05rem;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
        margin-bottom: 1rem;
    }

    .list-card ul {
        margin: 0.5rem 0 0 1.1rem;
        padding: 0;
    }

    .list-card li {
        margin-bottom: 0.5rem;
    }

    .insight-strip {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.75rem;
        margin: 0.8rem 0 1rem 0;
    }

    .insight-chip {
        border-radius: 18px;
        padding: 0.9rem;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.06);
    }

    .insight-label {
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.14em;
        color: #fca5a5 !important;
        font-weight: 900;
        margin-bottom: 0.35rem;
    }

    .insight-value {
        font-size: 1.12rem;
        font-weight: 800;
    }

    @media (max-width: 900px) {
        .stApp::before {
            display: none !important;
        }

        .block-container {
            padding-top: 0.65rem;
            padding-left: 0.8rem;
            padding-right: 0.8rem;
        }

        [data-testid="stSidebar"] {
            min-width: 100vw !important;
            width: 100vw !important;
        }

        [data-testid="stSidebar"][aria-expanded="false"] {
            min-width: 0 !important;
            width: 0 !important;
            margin-left: -100vw !important;
            transform: translateX(-100%) !important;
        }

        [data-testid="stTabs"] [data-baseweb="tab-list"] {
            border-radius: 18px;
            padding: 0.3rem;
            gap: 0.35rem;
        }

        button[data-baseweb="tab"] {
            padding: 0.6rem 0.75rem !important;
            font-size: 0.9rem !important;
        }

        .hero {
            min-height: 360px;
            padding: 1.35rem 1rem 1.1rem 1rem;
            border-radius: 22px;
        }

        .hero-title {
            font-size: 2rem;
            line-height: 0.95;
        }

        .hero-sub {
            font-size: 0.95rem;
            max-width: 100%;
        }

        .pill-row {
            gap: 0.45rem;
        }

        .pill {
            font-size: 0.75rem;
            padding: 0.45rem 0.65rem;
        }

        .feature-banner {
            min-height: 250px;
            padding: 1rem;
            border-radius: 20px;
        }

        .feature-title {
            font-size: 1.05rem;
        }

        .feature-text {
            font-size: 0.76rem;
        }

        .status-grid,
        .insight-strip {
            grid-template-columns: 1fr;
        }

        .feature-copy {
            width: min(100%, 100%);
            left: 56%;
            right: auto;
            top: 0.35rem;
            bottom: auto;
            transform: translateX(-50%);
        }

        .feature-copy.bottom-left {
            left: 0.7rem;
            right: 0.7rem;
            top: auto;
            bottom: 0.7rem;
            transform: none;
        }
    }
    </style>
    """, unsafe_allow_html=True)


def get_app_password() -> str:
    secret_password = ""
    try:
        secret_password = str(st.secrets.get("APP_PASSWORD", "")).strip()
    except Exception:
        secret_password = ""
    return os.getenv("APP_PASSWORD", secret_password).strip()


def require_app_password():
    app_password = get_app_password()
    if not app_password:
        return True

    unlocked = bool(st.session_state.get("app_unlocked"))
    st.markdown("---")
    st.markdown("### Admin Mode")

    if unlocked:
        st.success("Edit mode unlocked")
        if st.button("Lock Edit Mode"):
            st.session_state["app_unlocked"] = False
            st.rerun()
        return True

    entered = st.text_input("Edit password", type="password", placeholder="Enter password to edit", key="edit_password")
    if st.button("Unlock Edit Mode"):
        if hmac.compare_digest(entered, app_password):
            st.session_state["app_unlocked"] = True
            st.rerun()
        else:
            st.error("Wrong password.")

    st.caption("View mode is on. Anyone can look, but only unlocked admin mode can save changes.")
    return False


# =========================================================
# DATA
# =========================================================
def default_day() -> Dict[str, Any]:
    return {
        "water_oz": 0,
        "pages_read": 0,
        "diet_followed": False,
        "progress_picture": False,
        "workout_1_done": False,
        "workout_1_type": "",
        "workout_1_location": "",
        "workout_1_minutes": 45,
        "workout_2_done": False,
        "workout_2_type": "",
        "workout_2_location": "",
        "workout_2_minutes": 45,
        "notes": "",
        "weight": None,
        "calories": None,
        "protein": None,
        "carbs": None,
        "fats": None,
        "saved_workout": {},
        "discipline_score": 0,
        "water": 0,
        "pages": 0,
        "diet": False,
        "photo": False,
        "workout1": False,
        "workout2": False,
    }


def default_data() -> Dict[str, Any]:
    return {
        "profile": {
            "name": "Dez",
            "start_date": str(date.today()),
            "phase_name": "Built Different",
            "daily_water_goal_oz": 128,
            "daily_pages_goal": 10,
            "target_calories": 2393,
            "target_protein": 207,
            "target_carbs": 241,
            "target_fats": 66,
        },
        "days": {},
        "coach_chat": [
            {"role": "ai", "text": "Welcome back, Dez. Protect the streak and finish the day strong."}
        ],
    }


def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        data = default_data()
        save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        data = default_data()
        save_data(data)
        return data

    if not isinstance(data, dict):
        data = default_data()

    base = default_data()
    data.setdefault("profile", base["profile"])
    data.setdefault("days", {})
    data.setdefault("coach_chat", base["coach_chat"])

    for k, v in base["profile"].items():
        data["profile"].setdefault(k, v)

    if not isinstance(data["days"], dict):
        data["days"] = {}

    fixed_days = {}
    for day_key, raw in data["days"].items():
        clean = default_day()
        if isinstance(raw, dict):
            clean.update(raw)

        if "water" in clean and not clean.get("water_oz"):
            clean["water_oz"] = clean.get("water", 0)
        if "pages" in clean and not clean.get("pages_read"):
            clean["pages_read"] = clean.get("pages", 0)
        if "diet" in clean and not clean.get("diet_followed"):
            clean["diet_followed"] = clean.get("diet", False)
        if "photo" in clean and not clean.get("progress_picture"):
            clean["progress_picture"] = clean.get("photo", False)
        if "workout1" in clean and not clean.get("workout_1_done"):
            clean["workout_1_done"] = clean.get("workout1", False)
        if "workout2" in clean and not clean.get("workout_2_done"):
            clean["workout_2_done"] = clean.get("workout2", False)

        clean["water"] = clean.get("water_oz", 0)
        clean["pages"] = clean.get("pages_read", 0)
        clean["diet"] = clean.get("diet_followed", False)
        clean["photo"] = clean.get("progress_picture", False)
        clean["workout1"] = clean.get("workout_1_done", False)
        clean["workout2"] = clean.get("workout_2_done", False)

        fixed_days[day_key] = clean

    data["days"] = fixed_days
    return data


def save_data(data: Dict[str, Any]):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_day(data: Dict[str, Any], selected_day: date) -> Dict[str, Any]:
    key = str(selected_day)
    if key not in data["days"]:
        data["days"][key] = default_day()
    else:
        merged = default_day()
        merged.update(data["days"][key])
        data["days"][key] = merged

    d = data["days"][key]
    d["water"] = d.get("water_oz", 0)
    d["pages"] = d.get("pages_read", 0)
    d["diet"] = d.get("diet_followed", False)
    d["photo"] = d.get("progress_picture", False)
    d["workout1"] = d.get("workout_1_done", False)
    d["workout2"] = d.get("workout_2_done", False)
    return d


# =========================================================
# HELPERS
# =========================================================
def calc_score(day: Dict[str, Any], profile: Dict[str, Any]) -> int:
    score = 0
    water_goal = profile.get("daily_water_goal_oz", 128)
    pages_goal = profile.get("daily_pages_goal", 10)

    score += 20 if day.get("water_oz", 0) >= water_goal else int((day.get("water_oz", 0) / max(water_goal, 1)) * 20)
    score += 15 if day.get("pages_read", 0) >= pages_goal else int((day.get("pages_read", 0) / max(pages_goal, 1)) * 15)

    if day.get("diet_followed"):
        score += 20
    if day.get("progress_picture"):
        score += 10
    if day.get("workout_1_done"):
        score += 15
    if day.get("workout_2_done"):
        score += 15

    if day.get("workout_1_location", "").lower() == "outdoor" or day.get("workout_2_location", "").lower() == "outdoor":
        score += 5

    return min(score, 100)


def day_complete(day: Dict[str, Any], profile: Dict[str, Any]) -> bool:
    return (
        day.get("water_oz", 0) >= profile.get("daily_water_goal_oz", 128)
        and day.get("pages_read", 0) >= profile.get("daily_pages_goal", 10)
        and day.get("diet_followed", False)
        and day.get("progress_picture", False)
        and day.get("workout_1_done", False)
        and day.get("workout_2_done", False)
    )


def day_number(profile: Dict[str, Any], d: date) -> int:
    try:
        start = datetime.strptime(profile.get("start_date", str(date.today())), "%Y-%m-%d").date()
    except Exception:
        start = date.today()
    return (d - start).days + 1


def challenge_day_label(profile: Dict[str, Any], d: date) -> str:
    num = day_number(profile, d)
    return f"Day {num}" if num >= 1 else "Pre-start"


def current_streak(data: Dict[str, Any]) -> int:
    streak = 0
    cursor = date.today()
    while True:
        key = str(cursor)
        if key not in data["days"]:
            break
        if day_complete(data["days"][key], data["profile"]):
            streak += 1
            cursor -= timedelta(days=1)
        else:
            break
    return streak


def best_streak(data: Dict[str, Any]) -> int:
    if not data["days"]:
        return 0

    dates = sorted([datetime.strptime(k, "%Y-%m-%d").date() for k in data["days"].keys()])
    best = 0
    run = 0
    prev = None

    for d in dates:
        if day_complete(data["days"][str(d)], data["profile"]):
            if prev and d == prev + timedelta(days=1):
                run += 1
            else:
                run = 1
            best = max(best, run)
        else:
            run = 0
        prev = d
    return best


def quote() -> str:
    quotes = [
        "Burn fat. Build discipline.",
        "Every day finished clean is a vote for the man you want to become.",
        "You do not need perfect. You need complete.",
        "Hard days count more than easy days.",
        "Momentum loves people who keep showing up.",
    ]
    return random.choice(quotes)


def render_status_grid(items):
    blocks = []
    for title, value, done in items:
        state_class = "done" if done else "open"
        blocks.append(
            f'<div class="status-item {state_class}">'
            f'<div class="status-title">{escape(str(title))}</div>'
            f'<div class="status-value">{escape(str(value))}</div>'
            f'</div>'
        )
    st.markdown(f"<div class='status-grid'>{''.join(blocks)}</div>", unsafe_allow_html=True)


def render_list_card(title: str, items, empty_text: str):
    if items:
        body = "".join(f"<li>{escape(str(item))}</li>" for item in items)
        content = f"<ul>{body}</ul>"
    else:
        content = f"<div class='small-muted'>{escape(empty_text)}</div>"
    st.markdown(
        f'<div class="list-card"><div class="section-kicker">{escape(title)}</div>{content}</div>',
        unsafe_allow_html=True,
    )


def render_insight_strip(items):
    cards = []
    for label, value in items:
        cards.append(
            f'<div class="insight-chip">'
            f'<div class="insight-label">{escape(str(label))}</div>'
            f'<div class="insight-value">{escape(str(value))}</div>'
            f'</div>'
        )
    st.markdown(f"<div class='insight-strip'>{''.join(cards)}</div>", unsafe_allow_html=True)


def stat_card(label: str, value: str, sub: str):
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-label">{label}</div>
            <div class="stat-value">{value}</div>
            <div class="stat-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_card(kicker: str, title: str, sub: str):
    st.markdown(
        f"""
        <div class="glass-card">
            <div class="section-kicker">{kicker}</div>
            <div class="section-title">{title}</div>
            <div class="section-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero(profile: Dict[str, Any], selected_day: date, score_val: int, streak_val: int):
    style = background_style(
        HERO_IMG,
        "linear-gradient(100deg, rgba(0,0,0,0.74), rgba(0,0,0,0.28))"
    )

    st.markdown(
        f"""
        <div class="top-brand">
            <div class="brand-left">🔥 Dez 75 Hard</div>
            <div class="brand-right">Red Premium Edition</div>
        </div>

        <div class="hero" style="{style}">
            <div class="hero-eyebrow">Dez Performance System</div>
            <div class="hero-title">Burn Fat.<br>Build Muscle.<br>Stay Locked In.</div>
            <div class="hero-sub">
                Premium command center for Dez’s 75 Hard run — training, hydration, reading, nutrition, recovery, and streak protection.
            </div>
            <div class="pill-row">
                <span class="pill">Day {day_number(profile, selected_day)}</span>
                <span class="pill">{profile.get("phase_name", "Built Different")}</span>
                <span class="pill">Score: {score_val}/100</span>
                <span class="pill">Streak: {streak_val} days</span>
                <span class="pill">Water Goal: {profile.get("daily_water_goal_oz", 128)} oz</span>
                <span class="pill">Pages: {profile.get("daily_pages_goal", 10)}</span>
            </div>
            <div style="margin-top:1rem;color:#edf2f8;">{quote()}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_banner(title: str, text: str, image_path: str = "", red_block: bool = False, bg_size: str = "cover", bg_position: str = "center 28%", copy_class: str = ""):
    if red_block:
        st.markdown(
            f"""
            <div class="feature-banner red-block">
                <div class="feature-copy {copy_class}">
                    <div class="feature-title">{title}</div>
                    <div class="feature-text">{text}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        style = background_style(
            image_path,
            "linear-gradient(100deg, rgba(0,0,0,0.28), rgba(0,0,0,0.08))",
            size=bg_size,
            position=bg_position,
        )
        st.markdown(
            f"""
            <div class="feature-banner" style="{style}">
                <div class="feature-copy {copy_class}">
                    <div class="feature-title">{title}</div>
                    <div class="feature-text">{text}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def mini_banner(title: str, text: str, image_path: str):
    style = background_style(
        image_path,
        "linear-gradient(100deg, rgba(0,0,0,0.24), rgba(0,0,0,0.08))"
    )
    st.markdown(
        f"""
        <div class="mini-banner" style="{style}">
            <div style="font-size:1.45rem;font-weight:900;letter-spacing:-0.03em;margin-bottom:0.4rem;">{title}</div>
            <div class="small-muted">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def fallback_coach_response(msg: str, day: Dict[str, Any], profile: Dict[str, Any]) -> str:
    m = msg.lower()
    water_left = max(profile.get("daily_water_goal_oz", 128) - day.get("water_oz", 0), 0)
    pages_left = max(profile.get("daily_pages_goal", 10) - day.get("pages_read", 0), 0)
    score_val = calc_score(day, profile)

    if "date" in m or "today" in m:
        return f"Today is {date.today().strftime('%A, %B %d, %Y')}."
    if "how am i doing" in m or "score" in m or "status" in m:
        return f"Dez, your discipline score is {score_val}/100. You have {water_left} oz water and {pages_left} pages left."
    if "what do i have left" in m or "left" in m:
        items = []
        if water_left > 0:
            items.append(f"{water_left} oz water")
        if pages_left > 0:
            items.append(f"{pages_left} pages")
        if not day.get("diet_followed"):
            items.append("diet confirmation")
        if not day.get("progress_picture"):
            items.append("progress photo")
        if not day.get("workout_1_done"):
            items.append("workout 1")
        if not day.get("workout_2_done"):
            items.append("workout 2")
        if items:
            return "You still have: " + ", ".join(items) + "."
        return "You have nothing left. Finish clean."
    if "motivation" in m or "tough" in m:
        return "Do not negotiate with yourself, Dez. Finish the tasks, protect the streak, and earn the result."
    if "workout" in m:
        return "Train with intent. Pick one measurable win and beat it today."
    return "Lock in. Finish your tasks. Protect the streak."


def progress_df(data: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for k, d in sorted(data["days"].items()):
        try:
            dt = datetime.strptime(k, "%Y-%m-%d").date()
        except Exception:
            continue
        rows.append({
            "date": dt,
            "water_oz": d.get("water_oz", 0),
            "pages_read": d.get("pages_read", 0),
            "weight": d.get("weight"),
            "calories": d.get("calories"),
            "protein": d.get("protein"),
            "carbs": d.get("carbs"),
            "fats": d.get("fats"),
            "score": calc_score(d, data["profile"]),
            "complete": 1 if day_complete(d, data["profile"]) else 0,
        })
    return pd.DataFrame(rows)


EXERCISE_BANK = {
    "Push": {
        "Bodyweight": ["Push-ups - 4 x 15", "Pike push-ups - 4 x 10", "Bench dips - 4 x 12", "Tempo push-ups - 3 x 12"],
        "Dumbbells": ["DB bench press - 4 x 10", "Incline DB press - 3 x 10", "Shoulder press - 4 x 8", "Lateral raises - 4 x 15"],
        "Gym": ["Bench press - 4 x 6-8", "Incline press machine - 3 x 10", "Shoulder press machine - 3 x 8-10", "Rope pushdowns - 4 x 12"],
    },
    "Pull": {
        "Bodyweight": ["Door rows - 4 x 10", "Supermans - 4 x 15", "Reverse snow angels - 3 x 15", "Towel curls - 3 x 12"],
        "Dumbbells": ["1-arm rows - 4 x 10", "Hammer curls - 4 x 12", "Rear delt fly - 3 x 15", "DB RDL - 4 x 10"],
        "Gym": ["Lat pulldown - 4 x 10", "Seated cable row - 4 x 10", "Machine high row - 3 x 12", "EZ-bar curls - 4 x 10"],
    },
    "Legs": {
        "Bodyweight": ["Air squats - 5 x 20", "Walking lunges - 4 x 12 each", "Wall sit - 4 x 45 sec", "Glute bridges - 4 x 15"],
        "Dumbbells": ["Goblet squats - 4 x 10", "DB RDL - 4 x 10", "Bulgarian split squat - 3 x 8 each", "Calf raises - 4 x 20"],
        "Gym": ["Back squat - 4 x 5-8", "Romanian deadlift - 4 x 8", "Leg press - 3 x 12", "Leg curl - 3 x 12", "Leg extension - 3 x 15"],
    },
    "Cardio": {
        "Bodyweight": ["Outdoor brisk walk - 45 min", "Jog/walk intervals - 35 min", "Hill walk - 30 min", "Shadow boxing intervals - 10 rounds"],
        "Dumbbells": ["DB conditioning circuit - 5 rounds", "Farmer carry intervals - 6 rounds", "DB step-up circuit - 25 min"],
        "Gym": ["Incline treadmill walk - 45 min", "Stair climber - 25 min", "Bike intervals - 25 min", "Row machine intervals - 20 min"],
    },
    "Upper": {
        "Bodyweight": ["Push-ups - 4 x 15", "Inverted rows - 4 x 10", "Chair dips - 3 x 12", "Plank shoulder taps - 3 x 20"],
        "Dumbbells": ["DB bench press - 4 x 10", "DB rows - 4 x 10", "Shoulder press - 3 x 10", "Hammer curls - 3 x 12"],
        "Gym": ["Bench press - 4 x 6-8", "Lat pulldown - 4 x 10", "Cable row - 3 x 10", "Machine chest press - 3 x 10", "Cable curls - 3 x 12"],
    },
    "Full Body": {
        "Bodyweight": ["Circuit: squats, push-ups, lunges, mountain climbers x 5 rounds", "Bodyweight EMOM - 20 min", "Outdoor athletic circuit - 35 min"],
        "Dumbbells": ["DB squat to press - 4 x 10", "DB RDL - 4 x 10", "DB row - 4 x 10", "DB floor press - 3 x 12"],
        "Gym": ["Trap bar deadlift - 4 x 5", "Bench press - 3 x 8", "Lat pulldown - 3 x 10", "Leg press - 3 x 12", "Cable row - 3 x 12"],
    },
}


def build_workout(goal: str, focus: str, equipment: str, duration: int, intensity: str) -> Dict[str, Any]:
    pool = EXERCISE_BANK.get(focus, EXERCISE_BANK["Full Body"]).get(equipment, [])
    count = 3 if duration <= 30 else 4 if duration <= 45 else 5
    selected = random.sample(pool, k=min(count, len(pool)))
    return {
        "goal": goal,
        "focus": focus,
        "equipment": equipment,
        "duration": duration,
        "intensity": intensity,
        "warmup": ["Dynamic mobility x 4 min", "Activation warmup x 3 min"],
        "main": selected,
        "finisher": "Push pace for the last 5 minutes and finish with intent.",
        "note": f"{intensity} {focus.lower()} session. Keep transitions tight and form clean.",
    }


# =========================================================
# APP START
# =========================================================
inject_styles()
data = load_data()
profile = data["profile"]

with st.sidebar:
    st.markdown("## 🔥 Dez 75 Hard")
    st.caption("Red premium edition")

    selected_day = st.date_input("Selected day", value=date.today())
    current_day = get_day(data, selected_day)
    can_edit = require_app_password()

    st.markdown("---")
    st.markdown("### Quick Stats")
    st.write(f"**Current streak:** {current_streak(data)}")
    st.write(f"**Best streak:** {best_streak(data)}")
    st.write(f"**Day number:** {day_number(profile, selected_day)}")

    st.markdown("---")
    st.markdown("### Profile")
    profile["name"] = st.text_input("Name", value=profile.get("name", "Dez"), disabled=not can_edit)
    profile["phase_name"] = st.text_input("Phase / Motto", value=profile.get("phase_name", "Built Different"), disabled=not can_edit)
    profile["start_date"] = str(
        st.date_input(
            "75 Hard start date",
            value=datetime.strptime(profile.get("start_date", str(date.today())), "%Y-%m-%d").date()
            if profile.get("start_date") else date.today(),
            disabled=not can_edit
        )
    )

    st.markdown("### Goal Settings")
    profile["daily_water_goal_oz"] = st.number_input("Water goal (oz)", min_value=32, max_value=256, value=int(profile.get("daily_water_goal_oz", 128)), step=8, disabled=not can_edit)
    profile["daily_pages_goal"] = st.number_input("Pages goal", min_value=1, max_value=100, value=int(profile.get("daily_pages_goal", 10)), step=1, disabled=not can_edit)
    profile["target_calories"] = st.number_input("Calories target", min_value=1000, max_value=6000, value=int(profile.get("target_calories", 2393)), step=10, disabled=not can_edit)
    profile["target_protein"] = st.number_input("Protein target", min_value=50, max_value=400, value=int(profile.get("target_protein", 207)), step=1, disabled=not can_edit)
    profile["target_carbs"] = st.number_input("Carbs target", min_value=0, max_value=600, value=int(profile.get("target_carbs", 241)), step=1, disabled=not can_edit)
    profile["target_fats"] = st.number_input("Fats target", min_value=0, max_value=200, value=int(profile.get("target_fats", 66)), step=1, disabled=not can_edit)

if can_edit:
    save_data(data)

current_day = get_day(data, selected_day)
current_day["discipline_score"] = calc_score(current_day, profile)
if can_edit:
    save_data(data)

score_val = calc_score(current_day, profile)
streak_val = current_streak(data)

hero(profile, selected_day, score_val, streak_val)

tab_home, tab_checklist, tab_workouts, tab_macros, tab_calendar, tab_report, tab_charts, tab_coach = st.tabs([
    "🏠 Home",
    "✅ Checklist",
    "🏋️ Workout Generator",
    "🍽 Macros & Body",
    "🗓 Calendar",
    "📊 Weekly Report",
    "📈 Progress Charts",
    "🧠 Coach Chat",
])

# =========================================================
# HOME
# =========================================================
with tab_home:
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        stat_card("Day Number", str(day_number(profile, selected_day)), "Your position in the 75 Hard run")
    with s2:
        stat_card("Current Streak", str(streak_val), "Consecutive completed days")
    with s3:
        stat_card("Best Streak", str(best_streak(data)), "Best run so far")
    with s4:
        stat_card("Discipline Score", f"{score_val}/100", "Weighted score for today")

    b1, b2 = st.columns([1, 1.25])
    with b1:
        feature_banner(
            "Built in the work. Proven by the reps.",
            "Dez’s training system now feels more like a premium fitness brand — stronger visuals, sharper structure, and cleaner momentum.",
            image_path=WORKOUT_IMG if os.path.exists(WORKOUT_IMG) else HERO_IMG,
            bg_size="cover",
            bg_position="center center",
            copy_class="bottom-left",
        )
    with b2:
        feature_banner(
            "No excuses. Just work.",
            "Stay locked in and let the results follow.",
            image_path=COMMUNITY_IMG if os.path.exists(COMMUNITY_IMG) else WORKOUT_IMG,
            bg_size="cover",
            bg_position="center 34%",
        )

    m1, m2, m3 = st.columns(3)
    with m1:
        mini_banner("Today’s Mission", "Hydrate. Read. Train twice. Eat clean. Protect the streak.", MISSION_NATURE_IMG)
    with m2:
        mini_banner("Progress Zone", "Daily consistency compounds into visible change.", PROGRESS_IMG)
    with m3:
        mini_banner("Coach Energy", "Use the coach tab for accountability and next-step focus.", COACH_IMG if os.path.exists(COACH_IMG) else HERO_IMG)

    left, right = st.columns([1.25, 1])

    with left:
        section_card("Today", "Execution Summary", "Fast read on whether the day is trending strong or drifting.")

        water_goal = profile.get("daily_water_goal_oz", 128)
        pages_goal = profile.get("daily_pages_goal", 10)
        workouts_done = int(current_day.get("workout_1_done", False)) + int(current_day.get("workout_2_done", False))

        render_insight_strip([
            ("Hydration", f"{current_day.get('water_oz', 0)} / {water_goal} oz"),
            ("Reading", f"{current_day.get('pages_read', 0)} / {pages_goal} pages"),
            ("Workouts", f"{workouts_done} / 2 complete"),
        ])

        st.markdown("**Water Progress**")
        st.progress(min(current_day.get("water_oz", 0) / max(water_goal, 1), 1.0), text=f"{current_day.get('water_oz', 0)} / {water_goal} oz")

        st.markdown("**Reading Progress**")
        st.progress(min(current_day.get("pages_read", 0) / max(pages_goal, 1), 1.0), text=f"{current_day.get('pages_read', 0)} / {pages_goal} pages")

        st.markdown("**Workout Completion**")
        st.progress(workouts_done / 2, text=f"{workouts_done} / 2 workouts completed")

        st.markdown("### Mission Status")
        st.write("✅ Diet locked in" if current_day.get("diet_followed") else "⬜ Diet still open")
        st.write("✅ Progress photo done" if current_day.get("progress_picture") else "⬜ Progress photo still open")
        st.write(
            "✅ Outdoor workout logged"
            if current_day.get("workout_1_location", "").lower() == "outdoor" or current_day.get("workout_2_location", "").lower() == "outdoor"
            else "⬜ Outdoor workout not logged yet"
        )

        outdoor_logged = current_day.get("workout_1_location", "").lower() == "outdoor" or current_day.get("workout_2_location", "").lower() == "outdoor"
        complete_today = day_complete(current_day, profile)
        render_status_grid([
            ("Diet", "Locked in" if current_day.get("diet_followed") else "Still open", bool(current_day.get("diet_followed"))),
            ("Progress Photo", "Done" if current_day.get("progress_picture") else "Still open", bool(current_day.get("progress_picture"))),
            ("Outdoor Session", "Logged" if outdoor_logged else "Not logged yet", outdoor_logged),
            ("Day Finish", "Clean finish" if complete_today else "Still building", complete_today),
        ])

    with right:
        section_card("Focus", "Dez’s Command Panel", "Use this as your quick daily lock-in zone.")

        remaining = []
        if current_day.get("water_oz", 0) < water_goal:
            remaining.append(f"{water_goal - current_day.get('water_oz', 0)} oz water")
        if current_day.get("pages_read", 0) < pages_goal:
            remaining.append(f"{pages_goal - current_day.get('pages_read', 0)} pages")
        if not current_day.get("diet_followed"):
            remaining.append("diet confirmation")
        if not current_day.get("progress_picture"):
            remaining.append("progress photo")
        if not current_day.get("workout_1_done"):
            remaining.append("workout 1")
        if not current_day.get("workout_2_done"):
            remaining.append("workout 2")

        render_list_card("Remaining Items", remaining, "Nothing left. Clean finish.")

        st.markdown("**Saved workout**")
        sw = current_day.get("saved_workout", {})
        if sw:
            st.markdown(
                f"""
                <div class="glass-card">
                    <strong>{sw.get("focus", "Workout")}</strong> • {sw.get("duration", 45)} min<br>
                    <span class="small-muted">{sw.get("goal", "")} • {sw.get("equipment", "")} • {sw.get("intensity", "")}</span><br><br>
                    {sw.get("note", "")}
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("No saved generated workout yet for this day.")

        note = st.text_area("Daily note", value=current_day.get("notes", ""), height=130, placeholder="Write how the day felt, mood, wins, cravings, training notes...", disabled=not can_edit)
        if st.button("Save Daily Note", disabled=not can_edit):
            current_day["notes"] = note
            save_data(data)
            st.success("Daily note saved.")

# =========================================================
# CHECKLIST
# =========================================================
with tab_checklist:
    section_card("Daily Tracking", f"Checklist for {selected_day.strftime('%A, %b %d, %Y')}", "Log the essentials and protect the streak.")

    left, right = st.columns([1.1, 1])

    with left:
        current_day["water_oz"] = st.number_input("Water consumed (oz)", min_value=0, max_value=300, value=int(current_day.get("water_oz", 0)), step=1, disabled=not can_edit)
        current_day["pages_read"] = st.number_input("Pages read", min_value=0, max_value=100, value=int(current_day.get("pages_read", 0)), step=1, disabled=not can_edit)

        current_day["diet_followed"] = st.checkbox("Diet Followed", value=bool(current_day.get("diet_followed", False)), disabled=not can_edit)
        current_day["progress_picture"] = st.checkbox("Progress Photo", value=bool(current_day.get("progress_picture", False)), disabled=not can_edit)

        st.markdown("### Workout 1")
        current_day["workout_1_done"] = st.checkbox("Workout 1 done", value=bool(current_day.get("workout_1_done", False)), disabled=not can_edit)
        current_day["workout_1_type"] = st.selectbox("Workout 1 type", ["", "Strength", "HIIT", "Walk", "Run", "Bike", "Yoga", "Sports", "Custom"], index=["", "Strength", "HIIT", "Walk", "Run", "Bike", "Yoga", "Sports", "Custom"].index(current_day.get("workout_1_type", "") if current_day.get("workout_1_type", "") in ["", "Strength", "HIIT", "Walk", "Run", "Bike", "Yoga", "Sports", "Custom"] else ""), disabled=not can_edit)
        current_day["workout_1_location"] = st.selectbox("Workout 1 location", ["", "Outdoor", "Gym", "Home", "Other"], index=["", "Outdoor", "Gym", "Home", "Other"].index(current_day.get("workout_1_location", "") if current_day.get("workout_1_location", "") in ["", "Outdoor", "Gym", "Home", "Other"] else ""), disabled=not can_edit)
        current_day["workout_1_minutes"] = st.number_input("Workout 1 minutes", min_value=0, max_value=240, value=int(current_day.get("workout_1_minutes", 45)), step=1, disabled=not can_edit)

        st.markdown("### Workout 2")
        current_day["workout_2_done"] = st.checkbox("Workout 2 done", value=bool(current_day.get("workout_2_done", False)), disabled=not can_edit)
        current_day["workout_2_type"] = st.selectbox("Workout 2 type", ["", "Strength", "HIIT", "Walk", "Run", "Bike", "Yoga", "Sports", "Custom"], index=["", "Strength", "HIIT", "Walk", "Run", "Bike", "Yoga", "Sports", "Custom"].index(current_day.get("workout_2_type", "") if current_day.get("workout_2_type", "") in ["", "Strength", "HIIT", "Walk", "Run", "Bike", "Yoga", "Sports", "Custom"] else ""), key="w2type", disabled=not can_edit)
        current_day["workout_2_location"] = st.selectbox("Workout 2 location", ["", "Outdoor", "Gym", "Home", "Other"], index=["", "Outdoor", "Gym", "Home", "Other"].index(current_day.get("workout_2_location", "") if current_day.get("workout_2_location", "") in ["", "Outdoor", "Gym", "Home", "Other"] else ""), key="w2loc", disabled=not can_edit)
        current_day["workout_2_minutes"] = st.number_input("Workout 2 minutes", min_value=0, max_value=240, value=int(current_day.get("workout_2_minutes", 45)), step=1, key="w2mins", disabled=not can_edit)

        if st.button("Save Checklist", disabled=not can_edit):
            current_day["discipline_score"] = calc_score(current_day, profile)
            save_data(data)
            st.success("Checklist saved.")

    with right:
        sc = calc_score(current_day, profile)
        stat_card("Discipline Score", f"{sc}/100", "Updates live as you log the day")

        st.markdown("**Live Breakdown**")
        st.write(f"Water: {current_day.get('water_oz', 0)} / {profile.get('daily_water_goal_oz', 128)} oz")
        st.write(f"Pages: {current_day.get('pages_read', 0)} / {profile.get('daily_pages_goal', 10)}")
        st.write(f"Diet: {'Done' if current_day.get('diet_followed') else 'Open'}")
        st.write(f"Photo: {'Done' if current_day.get('progress_picture') else 'Open'}")
        st.write(f"Workout 1: {'Done' if current_day.get('workout_1_done') else 'Open'}")
        st.write(f"Workout 2: {'Done' if current_day.get('workout_2_done') else 'Open'}")

        notes = st.text_area("Checklist notes", value=current_day.get("notes", ""), height=160, key="checklistnotes", disabled=not can_edit)
        if st.button("Save Notes", disabled=not can_edit):
            current_day["notes"] = notes
            save_data(data)
            st.success("Notes saved.")

# =========================================================
# WORKOUT GENERATOR
# =========================================================
with tab_workouts:
    section_card("Training Engine", "Workout Generator", "Generate cleaner sessions based on focus, equipment, intensity, and time.")

    top1, top2 = st.columns([1, 1])
    with top1:
        feature_banner(
            "Train hard. Track harder.",
            "Build workout sessions that match your available equipment, your training goal, and how intense you want the day to be.",
            image_path=WORKOUT_IMG,
        )
    with top2:
        feature_banner(
            "Red Zone Performance",
            "Use saved sessions to make every day feel intentional instead of random.",
            red_block=True,
        )

    left, right = st.columns([1, 1.2])

    with left:
        goal = st.selectbox("Goal", ["Fat Loss", "Muscle Gain", "Performance", "Recovery", "Conditioning"])
        focus = st.selectbox("Focus", ["Push", "Pull", "Legs", "Cardio", "Upper", "Full Body"])
        equipment = st.selectbox("Equipment", ["Bodyweight", "Dumbbells", "Gym"])
        duration = st.slider("Duration", min_value=20, max_value=75, value=45, step=5)
        intensity = st.select_slider("Intensity", options=["Low", "Moderate", "High"], value="Moderate")

        if st.button("Generate Workout"):
            st.session_state["generated_workout"] = build_workout(goal, focus, equipment, duration, intensity)

        if st.button("Save Workout To Day", disabled=not can_edit):
            if "generated_workout" in st.session_state:
                current_day["saved_workout"] = st.session_state["generated_workout"]
                save_data(data)
                st.success("Workout saved to selected day.")
            else:
                st.warning("Generate a workout first.")

    with right:
        workout = st.session_state.get("generated_workout") or current_day.get("saved_workout", {})
        if workout:
            st.markdown(
                f"""
                <div class="glass-card">
                    <div class="section-kicker">Generated session</div>
                    <div class="section-title">{workout.get("focus", "")} • {workout.get("duration", 45)} min</div>
                    <div class="section-sub">{workout.get("goal", "")} • {workout.get("equipment", "")} • {workout.get("intensity", "")}</div>
                    <div style="margin-top:0.7rem;">{workout.get("note", "")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            c1, c2 = st.columns(2)
            with c1:
                st.markdown("### Warm-up")
                for item in workout.get("warmup", []):
                    st.markdown(f"- {item}")
                st.markdown("### Main")
                for item in workout.get("main", []):
                    st.markdown(f"- {item}")
            with c2:
                st.markdown("### Finisher")
                st.markdown(f"- {workout.get('finisher', '')}")
                st.markdown("### Coaching")
                st.markdown("- Pick one measurable win and beat it clean.")
        else:
            st.info("Generate a workout to see the session here.")

# =========================================================
# MACROS
# =========================================================
with tab_macros:
    section_card("Nutrition & Body", "Macros + Weight Tracking", "Stay aligned with your body comp targets and recovery.")

    top1, top2 = st.columns([1, 1])
    with top1:
        feature_banner(
            "Fuel the build.",
            "Log calories, protein, carbs, fats, and bodyweight so your training has nutrition behind it.",
            red_block=True,
        )
    with top2:
        feature_banner(
            "Progress is measurable.",
            "The more clean data you log, the more useful your trends become.",
            image_path=PROGRESS_IMG,
        )

    left, right = st.columns(2)

    with left:
        current_day["weight"] = st.number_input("Weight", min_value=0.0, max_value=1000.0, value=float(current_day.get("weight") or 0.0), step=0.1, format="%.1f", disabled=not can_edit)
        current_day["calories"] = st.number_input("Calories", min_value=0, max_value=10000, value=int(current_day.get("calories") or 0), step=1, disabled=not can_edit)
        current_day["protein"] = st.number_input("Protein (g)", min_value=0, max_value=500, value=int(current_day.get("protein") or 0), step=1, disabled=not can_edit)
        current_day["carbs"] = st.number_input("Carbs (g)", min_value=0, max_value=1000, value=int(current_day.get("carbs") or 0), step=1, disabled=not can_edit)
        current_day["fats"] = st.number_input("Fats (g)", min_value=0, max_value=300, value=int(current_day.get("fats") or 0), step=1, disabled=not can_edit)

        if st.button("Save Macros & Weight", disabled=not can_edit):
            save_data(data)
            st.success("Macros and weight saved.")

    with right:
        tc = profile.get("target_calories", 2393)
        tp = profile.get("target_protein", 207)
        tcarb = profile.get("target_carbs", 241)
        tf = profile.get("target_fats", 66)

        st.markdown("**Calories**")
        st.progress(min((current_day.get("calories") or 0) / max(tc, 1), 1.0), text=f"{current_day.get('calories') or 0} / {tc}")

        st.markdown("**Protein**")
        st.progress(min((current_day.get("protein") or 0) / max(tp, 1), 1.0), text=f"{current_day.get('protein') or 0} / {tp} g")

        st.markdown("**Carbs**")
        st.progress(min((current_day.get("carbs") or 0) / max(tcarb, 1), 1.0), text=f"{current_day.get('carbs') or 0} / {tcarb} g")

        st.markdown("**Fats**")
        st.progress(min((current_day.get("fats") or 0) / max(tf, 1), 1.0), text=f"{current_day.get('fats') or 0} / {tf} g")

# =========================================================
# CALENDAR
# =========================================================
with tab_calendar:
    section_card("Calendar View", "Monthly Consistency Map", "See how cleanly you are stacking days.")

    month = st.selectbox("Month", list(range(1, 13)), index=selected_day.month - 1)
    year = st.number_input("Year", min_value=2024, max_value=2100, value=selected_day.year, step=1)

    heads = st.columns(7)
    for i, h in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        with heads[i]:
            st.markdown(f"<div class='calendar-head'>{h}</div>", unsafe_allow_html=True)

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)

    for week in weeks:
        cols = st.columns(7)
        for i, n in enumerate(week):
            with cols[i]:
                if n == 0:
                    st.markdown("<div class='calendar-empty'></div>", unsafe_allow_html=True)
                else:
                    d = date(year, month, n)
                    dday = get_day(data, d)
                    sc = calc_score(dday, profile)
                    challenge_day = challenge_day_label(profile, d)
                    label = "✅ Complete" if day_complete(dday, profile) else "⚡ Strong" if sc >= 70 else "• Started" if sc > 0 else "— Empty"
                    st.markdown(
                        f"""
                        <div class='calendar-box'>
                            <strong>{n}</strong><br>
                            <span class='small-muted'>{challenge_day}</span><br>
                            <span class='small-muted'>{label}</span><br>
                            <span class='small-muted'>Score: {sc}</span><br>
                            <span class='small-muted'>Water: {dday.get("water_oz", 0)} oz</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

# =========================================================
# WEEKLY REPORT
# =========================================================
with tab_report:
    section_card("Weekly Analytics", "7-Day Report Card", "Review adherence, momentum, and where execution slipped.")

    end = st.date_input("Weekly report ending on", value=date.today(), key="week_end")
    start = end - timedelta(days=6)

    rows = []
    for i in range(7):
        d = start + timedelta(days=i)
        dday = get_day(data, d)
        rows.append({
            "Date": str(d),
            "Day": challenge_day_label(profile, d),
            "Score": calc_score(dday, profile),
            "Complete": "Yes" if day_complete(dday, profile) else "No",
            "Water": dday.get("water_oz", 0),
            "Pages": dday.get("pages_read", 0),
            "Workouts": int(dday.get("workout_1_done", False)) + int(dday.get("workout_2_done", False)),
        })

    wdf = pd.DataFrame(rows)
    c1, c2, c3 = st.columns(3)
    with c1:
        stat_card("Completed Days", f"{(wdf['Complete'] == 'Yes').sum()}/7", "Days fully closed")
    with c2:
        stat_card("Average Score", f"{round(wdf['Score'].mean(), 1)}", "Weekly discipline average")
    with c3:
        stat_card("Average Water", f"{round(wdf['Water'].mean(), 1)} oz", "Average daily hydration")

    st.dataframe(wdf, use_container_width=True, hide_index=True)

# =========================================================
# CHARTS
# =========================================================
with tab_charts:
    section_card("Visual Progress", "Trend Lines", "See whether your effort is tightening up over time.")

    df = progress_df(data)
    if df.empty:
        st.info("Log a few days first and your charts will show up here.")
    else:
        choice = st.selectbox("Chart view", ["score", "water_oz", "pages_read", "weight", "calories", "protein", "carbs", "fats"])
        chart_df = df[["date", choice]].dropna()
        if not chart_df.empty:
            st.line_chart(chart_df.set_index("date"))
        comp_df = df[["date", "complete"]].dropna()
        if not comp_df.empty:
            st.bar_chart(comp_df.set_index("date"))

# =========================================================
# COACH
# =========================================================
with tab_coach:
    section_card("Mindset", "Coach Chat", "A sharper accountability coach using your current day stats.")

    top1, top2 = st.columns([1, 1])
    with top1:
        feature_banner(
            "Stay coached.",
            "Use this area like a locker-room accountability tool when your day starts drifting.",
            image_path=COACH_IMG if os.path.exists(COACH_IMG) else HERO_IMG,
        )

    for msg in data.get("coach_chat", []):
        if msg.get("role") == "user":
            st.markdown(f"<div class='coach-user'><strong>You:</strong><br>{msg.get('text', '')}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='coach-ai'><strong>Coach:</strong><br>{msg.get('text', '')}</div>", unsafe_allow_html=True)

    user_msg = st.text_input("Message the coach", placeholder="Ask for motivation, status, what is left, workout help...", disabled=not can_edit)
    cc1, cc2 = st.columns([1, 1])
    with cc1:
        if st.button("Send to Coach", disabled=not can_edit):
            if user_msg.strip():
                data["coach_chat"].append({"role": "user", "text": user_msg.strip()})
                reply = fallback_coach_response(user_msg.strip(), current_day, profile)
                data["coach_chat"].append({"role": "ai", "text": reply})
                save_data(data)
                st.rerun()
    with cc2:
        if st.button("Clear Chat", disabled=not can_edit):
            data["coach_chat"] = [{"role": "ai", "text": "Chat reset. Good. Now lock back in and finish the day right."}]
            save_data(data)
            st.rerun()

    st.markdown("### Quick Coach Prompts")
    pc1, pc2, pc3, pc4 = st.columns(4)
    prompts = [
        "How am I doing today?",
        "What do I have left?",
        "Give me tough motivation",
        "What should I do next right now?",
    ]
    cols = [pc1, pc2, pc3, pc4]
    for col, prompt in zip(cols, prompts):
        with col:
            if st.button(prompt, disabled=not can_edit):
                data["coach_chat"].append({"role": "user", "text": prompt})
                reply = fallback_coach_response(prompt, current_day, profile)
                data["coach_chat"].append({"role": "ai", "text": reply})
                save_data(data)
                st.rerun()

if can_edit:
    save_data(data)

st.markdown("<div class='footer-note'>Built for discipline, momentum, and clean execution.</div>", unsafe_allow_html=True)
