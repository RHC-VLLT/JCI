import streamlit as st
import os
import base64

# --- CONSTANTES ---
LOGO_PATH = "../assets/logo.png"  # Ajustez le nom si c'est Logo_JCI_1.png
BG_PATH = "../assets/Acceuil_Pic_1_Page_1.jpg"
SITE_BG_URL = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop"

# --- FONCTION DE CHARGEMENT D'IMAGE ---
def load_base64_image(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# --- CSS GLOBAL ---
def inject_css(bg_base64_url=None):
    # Si une image locale est trouvée, on l'utilise, sinon l'URL internet
    bg_css = f"url('data:image/jpeg;base64,{bg_base64_url}')" if bg_base64_url else f"url('{SITE_BG_URL}')"
    
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF !important;
        background-color: transparent !important;
    }}
    
    /* Background Overlay */
    .stApp::before {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-image: {bg_css};
        background-size: cover; background-position: center; opacity: 0.6; z-index: -2; background-color: #000000;
    }}
    .stApp::after {{
        content: ""; position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
        background-color: #000000; opacity: 0.80; z-index: -1;
    }}

    /* Navbar */
    .modern-navbar-container {{ display: flex; justify-content: center; align-items: center; height: 100%; margin-top: 0.5%; }}
    .modern-navbar-container a {{ color: #FFFFFF; margin: 0 1%; padding: 10px 10%; text-decoration: none; font-size: 1.8rem; font-weight: 700; transition: all 0.3s; border-radius: 4px; }}
    .modern-navbar-container a:hover {{ background-color: rgba(215, 0, 29, 0.2); color: #D7001D; }}
    .modern-navbar-container a.active {{ color: #D7001D; border-bottom: 3px solid #D7001D; }}

    /* Inputs & Buttons */
    div[data-baseweb="input"], div[data-baseweb="select"] {{ background-color: #1a1a1a !important; border: 1px solid #333; border-radius: 50px !important; opacity: 0.9; }}
    div.stButton > button {{ color: white !important; background-color: #D7001D !important; border: 1px solid #D7001D !important; width: 100%; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }}
    div.stButton > button:hover {{ background-color: transparent !important; color: #D7001D !important; }}

    /* Hero Section */
    .hero {{ width: 100%; height: 85vh; background-size: cover; background-position: center; position: relative; display: flex; align-items: center; justify-content: flex-end; padding-right: 8%; margin-top: 20px; box-shadow: 0px 10px 30px -10px rgba(0,0,0,0.8); }}
    .hero-overlay {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: linear-gradient(270deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 100%); }}
    .hero-content {{ position: relative; z-index: 2; max-width: 600px; text-align: right; }}
    .hero-title {{ font-size: 3.8rem; font-weight: 800; line-height: 1.1; text-transform: uppercase; margin-bottom: 20px; text-shadow: 2px 2px 4px rgba(0,0,0,0.5); }}
    
    /* Cards */
    .movie-card-xl {{ flex: 1; min-width: 0; margin: 0 5px; background-color: #0a0a0a; border: 1px solid #222; border-radius: 15px; height: 680px; position: relative; overflow: hidden; transition: all 0.4s ease; }}
    .movie-card-xl:hover {{ transform: translateY(-5px); border-color: #D7001D !important; }}
    
    /* Utility */
    .btn-main {{ background-color: #D7001D; padding: 14px 35px; text-decoration: none; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; border-radius: 4px; color: white !important; border: 1px solid #D7001D; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }}
    .btn-main:hover {{ background-color: transparent; color: #D7001D !important; }}
    header, #MainMenu, footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)