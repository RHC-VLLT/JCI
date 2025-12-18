import streamlit as st
import os
import base64

# --- CONSTANTES ---
SITE_BG_URL = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop"
BG_PATH = "../assets/popcorn.jpg"

def load_base64_image(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return None

def inject_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800;900&family=Oswald:wght@700&display=swap');

    /* CONFIGURATION GLOBALE */
    html, body, [class*="css"], .stApp {{
        font-family: 'Montserrat', sans-serif;
        color: #FFFFFF ;
    }}
    
    /* FOND IMMERSIF FIXE */
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), url('{SITE_BG_URL}');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    /* HEADER NAVIGATION : LOGO TEXTE "JUST CREUSE IT" */
    div.stButton > button[key="logo_home"] {{
        background-color: transparent ;
        border: none ;
        color: #D7001D ;
        font-family: 'Oswald', sans-serif ;
        font-size: 2.5rem ; /* Taille augmentée pour l'effet logo */
        font-weight: 900 ;
        letter-spacing: -1.5px ;
        text-transform: uppercase ;
        padding: 0 ;
        transition: 0.3s ease-in-out ;
        line-height: 1 ;
    }}
    div.stButton > button[key="logo_home"]:hover {{
        color: #ff4d4d ;
        transform: scale(1.03);
        text-shadow: 0px 0px 15px rgba(215, 0, 29, 0.4);
    }}

    /* AUTRES BOUTONS DE NAVIGATION (FILMS / ACTEURS) */
    div.stButton > button[kind="secondary"] {{
        background-color: transparent ;
        border: none ;
        color: white ;
        font-weight: 700 ;
        font-size: 1rem ;
        text-transform: uppercase ;
        margin-top: 18px ;
    }}
    div.stButton > button[kind="secondary"]:hover {{
        color: #D7001D ;
    }}

    /* BOUTONS ROUGES DÉTAILS */
    div.stButton > button[kind="primary"] {{ 
        color: white ; 
        background-color: #D7001D ; 
        border: none ; 
        width: 100%; 
        font-weight: 800; 
        text-transform: uppercase; 
        border-radius: 0 0 12px 12px ;
        margin-top: -12px ; 
        height: 45px ;
    }}

    /* AFFICHES FILMS */
    .movie-poster-img {{
        width: 100%;
        border-radius: 12px 12px 0 0 ;
        object-fit: cover;
        aspect-ratio: 2/3;
        display: block;
        border: 1px solid rgba(255,255,255,0.1);
    }}

    /* VISUEL CASTING RONDS */
    .cast-img {{
        width: 110px; height: 110px;
        border-radius: 50%; object-fit: cover;
        border: 3px solid #D7001D;
        margin: 0 auto 10px auto;
        display: block;
        box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }}

    header, footer, #MainMenu {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)