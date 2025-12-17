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
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def inject_css():
    bg_64 = load_base64_image(BG_PATH)
    bg_css_val = f"data:image/jpeg;base64,{bg_64}" if bg_64 else SITE_BG_URL

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&display=swap');

    /* CONFIGURATION GLOBALE */
    html, body, [class*="css"], .stApp {{
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF !important;
        background-color: #1a1a1a !important;
    }}
    
    /* FOND IMMERSIF */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: url('{SITE_BG_URL}'); 
        background-size: cover; background-position: center; 
        opacity: 0.15; z-index: -2;
    }}
    .stApp::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #000000; opacity: 0.85; z-index: -1;
    }}

    /* HEADER NAVIGATION */
    div.stButton > button[kind="secondary"] {{
        background-color: transparent !important;
        border: none !important;
        color: white !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        text-transform: uppercase !important;
        transition: 0.3s !important;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        color: #D7001D !important;
        transform: translateY(-2px);
    }}

    /* BOUTONS ROUGES COLLÉS (STYLE DISNEY) */
    div.stButton > button[kind="primary"] {{ 
        color: white !important; 
        background-color: #D7001D !important; 
        border: none !important; 
        width: 100%; 
        font-weight: 800; 
        text-transform: uppercase; 
        border-radius: 0 0 12px 12px !important;
        margin-top: -12px !important; /* COMPRESSION POUR COLLER À L'IMAGE */
        height: 45px !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        background-color: #ff0022 !important;
    }}
    
    /* HERO BANNER */
    .hero {{ 
        width: 100%; height: 70vh; 
        background-image: url('{bg_css_val}');
        background-size: cover; background-position: center; 
        display: flex; align-items: center; justify-content: flex-end; 
        padding-right: 8%; border-radius: 20px; overflow: hidden;
    }}
    .hero-title {{ 
        font-size: 3.8rem; font-weight: 900; line-height: 1.1; 
        text-transform: uppercase; text-align: right;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.8);
    }}
    
    /* CARTES FILMS */
    .movie-card-container {{
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }}

    .movie-poster-img {{
        width: 100%;
        border-radius: 12px 12px 0 0 !important;
        object-fit: cover;
        aspect-ratio: 2/3;
        display: block;
        border: 1px solid #333;
    }}

    header, footer, #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)