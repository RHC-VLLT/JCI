import streamlit as st
import os
import base64

# --- CONSTANTES ---
SITE_BG_URL = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop"
LOGO_PATH = "../assets/Logo_JCI_1.png"
BG_PATH = "../assets/Acceuil_Pic_1_Page_1.jpg"

def load_base64_image(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def inject_css(bg_base64_url=None):
    bg_css = f"url('{SITE_BG_URL}')"
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF !important;
        background-color: transparent !important;
    }}
    
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: {bg_css};
        background-size: cover; background-position: center; opacity: 0.6; z-index: -2; background-color: #000000;
    }}
    .stApp::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #000000; opacity: 0.80; z-index: -1;
    }}

    /* NAVIGATION MODERNE & LÉGÈRE */
    div.stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        transition: 0.3s !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        color: #D7001D !important;
        transform: translateY(-2px);
    }}

    /* BOUTONS ROUGES RECTANGULAIRES (POUR DETAILS ET DECOUVRIR) */
    div.stButton > button[kind="primary"] {{ 
        color: white !important; background-color: #D7001D !important; border: 1px solid #D7001D !important; 
        width: 100%; font-weight: 700; text-transform: uppercase; border-radius: 4px !important;
    }}
    
    /* Hero Banner */
    .hero {{ width: 100%; height: 70vh; background-size: cover; background-position: center; position: relative; display: flex; align-items: center; justify-content: flex-end; padding-right: 8%; }}
    .hero-title {{ font-size: 3.5rem; font-weight: 800; text-transform: uppercase; text-align: right; }}
    
    /* Movie Card */
    .movie-card-xl {{ background-color: #0a0a0a; border: 1px solid #222; border-radius: 10px; height: 550px; overflow: hidden; position: relative; }}
    
    /* Style Casting */
    .cast-bubble {{ text-align: center; }}
    .cast-img {{ width: 80px; height: 80px; border-radius: 50%; object-fit: cover; border: 2px solid #D7001D; margin-bottom: 5px; }}
    
    header, #MainMenu, footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)