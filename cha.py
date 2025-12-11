import streamlit as st
import os
import base64

# ==========================
# 1. Configuration page
# ==========================
st.set_page_config(
    page_title="Just Creuse It - Cinéma",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================
# 2. Paths et utilitaires
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(BASE_DIR, "assets")
LOGO_PATH = os.path.join(ASSETS, "Logo_JCI_1.png")
BG_PATH = os.path.join(ASSETS, "Acceuil_Pic_1_Page_1.jpg")

def load_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def get_image_b64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return f.read()

logo_b64 = load_base64(LOGO_PATH)
bg_b64 = load_base64(BG_PATH)

logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
bg_url = f"data:image/jpeg;base64,{bg_b64}" if bg_b64 else ""

# ==========================
# 3. CSS global et Nouvelle Navbar (Moderne et Centrée)
# ==========================

# URL de l'image de fond "Salle de Ciné Royal"
site_bg_url = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

st.markdown(f"""
<style>
/* --- NOUVEAU NAVBAR STYLING (Moderne et Centrée) --- */
.modern-navbar-container {{
    display: flex;
    justify-content: center; /* Centre les liens de navigation */
    align-items: center;
    space-between: 20%;
    height: 100%;
    margin-top: 10px; /* Petit espace sous la séparation */
}}
.modern-navbar-container a {{
    color: #FFFFFF;
    margin: 0 2.5%; 
    space-between: 20%;
    padding: 10px 180px; /* Plus d'espace pour un look moderne et gros */
    text-decoration: none;
    font-size: 2rem; /* TAILLE AUGMENTÉE pour Accueil/Films/etc. */
    font-weight: 700; /* Plus gras */
    transition: all 0.3s;
    border-radius: 4px;
    margin: 0 5px; 
}}
.modern-navbar-container a:hover {{
    background-color: rgba(215, 0, 29, 0.2);
    color: #D7001D;
}}
.modern-navbar-container a.active {{
    color: #D7001D;
    border-bottom: 3px solid #D7001D; /* Soulignement moderne pour l'actif */
}}
/* --- Fin du nouveau NAVBAR STYLING --- */


/* Style général déjà existant */
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

/* --- CONFIGURATION GÉNÉRALE --- */
html, body, [class*="css"], .stApp {{
    font-family: 'Montserrat', sans-serif;
    color: #FFFFFF !important;
    background-color: transparent !important;
}}

/* --- COUCHE 1 : L'IMAGE DE FOND (Tout au fond) --- */
.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-image: url('{site_bg_url}');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    opacity: 0.6;
    z-index: -2;
    background-color: #000000;
}}

/* --- COUCHE 2 : LE FILTRE NOIR (Par dessus l'image) --- */
.stApp::after {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-color: #000000;
    opacity: 0.80;
    z-index: -1;
}}

/* --- TYPOGRAPHIE --- */
.stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown li, .stMarkdown span {{
    color: #FFFFFF !important;
}}
.stCaption {{
    color: #cccccc !important;
}}

/* --- CHAMPS DE SAISIE GÉNÉRAUX --- */
div[data-baseweb="input"] {{
    background-color: #1a1a1a !important;
    border: 1px solid #333;
    border-radius: 4px;
    opacity: 0.9;
}}
div[data-baseweb="input"] input {{
    color: white !important;
}}

/* --- BOUTON ROUGE --- */
div.stButton > button {{
    color: white !important;
    background-color: #D7001D !important;
    border: 1px solid #D7001D !important;
    width: 100%;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
}}
div.stButton > button:hover {{
    background-color: transparent !important;
    border: 1px solid #D7001D !important;
    color: #D7001D !important;
}}

/* --- HERO SECTION --- */
.hero {{
    width: 100%;
    height: 85vh;
    background-image: url('{bg_url}');
    background-size: cover;
    background-position: center;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: flex-end;
    padding-right: 8%;
    margin-top: 20px;
    box-shadow: 0px 10px 30px -10px rgba(0,0,0,0.8);
}}
.hero-overlay {{
    position: absolute;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: linear-gradient(270deg, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 100%);
}}
.hero-content {{
    position: relative;
    z-index: 2;
    max-width: 600px;
    text-align: right;
}}
.hero-title {{
    font-size: 3.8rem;
    font-weight: 800;
    line-height: 1.1;
    text-transform: uppercase;
    margin-bottom: 20px;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
}}
/* La classe hero-desc a été retirée du HTML dans la Section 5 */
.btn-main {{
    background-color: #D7001D;
    padding: 14px 35px;
    text-decoration: none;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-radius: 4px;
    color: white !important;
    border: 1px solid #D7001D;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}}
.btn-main:hover {{
    background-color: transparent;
    color: #D7001D !important;
}}

header {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


# ==========================
# 4. BARRE DE NAVIGATION HTML (Logo + Liens Centrés)
# ==========================

# Utilisation de trois colonnes : 1 (Logo) | 3 (Liens Centrés) | 1 (Espace Vide/Bouton)
col_logo, col_nav_center, col_spacer = st.columns([1, 3, 1])

with col_logo:
    if logo_url:
        # Logo cliquable pour recharger la page (retour à l'accueil)
        st.markdown(f"""
        <a href="#" onclick="window.location.reload();" style="display:flex; align-items:center; height:100%;">
            <img src="{logo_url}" width="400" style="vertical-align:middle;"> 
        </a>
        """, unsafe_allow_html=True)
    else:
        # LOGO DE SECOURS (Si l'image n'est pas trouvée, utilise le style 4em demandé)
        st.markdown("""
        <div style="color: #D7001D; font-size: 4em; font-weight: 800; line-height: 1.1; text-transform: uppercase;">
            JUST CREUSE IT
        </div>
        """, unsafe_allow_html=True)

with col_nav_center:
    # Conteneur centré pour les liens
    st.markdown("""
    <div class="modern-navbar-container">
        <a href="#" class="active">Accueil</a>
        <a href="#">Films</a>
        <a href="#">Genre</a>
        <a href="#">Acteurs</a>
    </div>
    """, unsafe_allow_html=True)

with col_spacer:
    # Espace vide ou un bouton/icône si nécessaire (par exemple, Log In ou Recherche)
    # Exemple d'icône:
    st.markdown("""
    <div style="display:flex; justify-content:flex-end; align-items:center; height:100%; padding-right:10px;">
        <a href="#" style="color:white; font-size:1.8rem; text-decoration:none;">👤</a>
    </div>
    """, unsafe_allow_html=True)


st.markdown("---") # Garder la ligne séparatrice pour l'esthétique

# ==========================
# 5. Section Hero
# ==========================
st.markdown(f"""
<div class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div>
        <a href="#recherche" class="btn-main">Le Film Parfait à la Carte >>></a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================
# 6. Section Recherche (Maintenue comme section de recherche principale)
# ==========================
st.markdown("<div id='recherche'></div>", unsafe_allow_html=True)
st.markdown("<br><h3 style='text-align:center; color:white;'>TROUVEZ VOTRE FILM COUP DE COEUR !</h3><br>", unsafe_allow_html=True)

# --- CSS POUR LE CHAMP DE TEXTE (Section 6) ---
st.markdown("""
<style>
/* Force le fond en blanc pour l'input de la section 6 */
.stApp .css-1cpx41z div[data-baseweb="input"] { 
    background-color: white !important;
    border: 1px solid #ccc !important;
}
/* Force le texte saisi en noir pour l'input de la section 6 */
.stApp .css-1cpx41z div[data-baseweb="input"] input { 
    color: black !important;
    -webkit-text-fill-color: black !important; 
    caret-color: black !important;
}
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.text_input("", placeholder="Rechercher par titre, acteur, genre...", label_visibility="collapsed", key="section_6_search")
    if st.button("SURPRENEZ-MOI", use_container_width=True, key="surprise_btn"):
        st.write("Recherche en cours...")

st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)

# ==========================
# 7. Section Recommandations Top 5 (Titre Rouge, Dimensions standardisées, Image complète)
# ==========================

st.set_page_config(layout="wide")


# TITRE centré
st.markdown("<h1 style='text-align: center;'> Top 5 des films pour vous </h1>", unsafe_allow_html=True)
st.write("---")


# 5 emplacements des films ---


# !!!!!! besoin de mettre le lien du poster!!!!!!!


poster_a_afficher = "https://image.tmdb.org/t/p/w500"


films = [
   {
       "titre": "CHARLOTTE AUX FRAISES : LE FILM",
       "annee": 2006,
       "pays": "US",
       "genres": "Animation, Famille, Comédie",
       "poster_path": "/8QVDXDiOGHRcAD4oM6MXjE0osSj.jpg",
       "top": 1
   },
   {
       "titre": "AVATAR: THE WAY OF WATER",
       "annee": 2025,
       "pays": "US",
       "genres": "Fantastique, Drame, Action, Fantastique",
       "poster_path": "/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
       "top": 2
   },
   {
       "titre": "AVENGERS: INFINITY WAR",
       "annee": 2025,
       "pays": "US",
       "genres": "Fantastique, Drame, Action, Comédie",
       "poster_path": "/8QVDXDiOGHRcAD4oM6MXjE0osSj.jpg",
       "top": 3
   },
   {
       "titre": "LE COMTE DE MONTE-CRISTO",
       "annee": 2024,
       "pays": "FR",
       "genres": "Action, Aventure, Drame",
       "poster_path": "/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
       "top": 4
   },
   {
       "titre": "CINQUIEME FILM (Exemple)",
       "annee": 2024,
       "pays": "FR",
       "genres": "Drame, Bloc Buster",
       "poster_path": "/8QVDXDiOGHRcAD4oM6MXjE0osSj.jpg",
       "top": 5
   }
]


# creation de colonnes avec boucle
# a chaque film afficher le film
# l'image
# année et pays?????
# genrte de films
# details fils


cols = st.columns(5)


for i, film in enumerate(films):
   with cols[i]:
       st.subheader(f"{film['top']}")
      
       # Afficr l'image du film
       st.image(poster_a_afficher + film["poster_path"], use_container_width=True)
       st.write("ETOILE---> note film à mettre  ")
       st.write(f"**{film['annee']}** | {film['pays']}")
       st.write(f"*{film['genres']}*")
      
       # Le bouton simple pour les détails
       st.button("Voir détails du film", key=f"details_{film['top']}")
          
# config bottons


st.write("---")

# ==========================
# 8. Détails du Film (3 colonnes alignées en hauteur - Image complète ajustée)
# ==========================
st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)
st.markdown("### Détails du Film recommandé")
st.markdown("<div style='height:2px;width:50px;background:#333;margin-bottom:20px;'></div>", unsafe_allow_html=True)

# Création de 3 colonnes
col_affiche, col_video, col_infos = st.columns([1, 2, 2])

# URL de l'image
url_affiche = "https://fr.web.img6.acsta.net/pictures/22/11/02/14/49/4565071.jpg"

# --- COLONNE 1 : L'AFFICHE (Hauteur fixée à 300px + Image complète) ---
with col_affiche:
    st.markdown(f"""
    <div style="height: 300px; width: 100%; background-color: #FFFFFF; border-radius: 5px; display: flex; align-items: center; justify-content: center; overflow: hidden; box-shadow: 0 4px 8px rgba(0,0,0,0.5);">
        <img src="{url_affiche}" 
            style="height: 100%; width: 100%; object-fit: contain;">
    </div>
    """, unsafe_allow_html=True)

# --- COLONNE 2 : LA BANDE-ANNONCE (Hauteur 300px) ---
with col_video:
    st.markdown("""
    <div style="display: flex; align-items: center; justify-content: center; height: 100%;">
        <iframe width="100%" height="300" src="https://www.youtube.com/embed/5PSNL1qE6VY" 
        title="Bande-annonce" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen
        style="border-radius: 5px; box-shadow: 0 4px 8px rgba(0,0,0,0.5);"></iframe>
    </div>
    """, unsafe_allow_html=True)

# --- COLONNE 3 : LES INFOS DETAILLEES DU FILM ---
with col_infos:
    st.markdown("**TITRE :** ex: Avatar")
    st.markdown("**ANNÉE :** ex: 2025")
    st.markdown("**PAYS :** ex: US")
    st.markdown("**DURÉE :** ex: 162 min")
    st.markdown("**GENRE :** ex: Science-Fiction")
    st.markdown("**NOTE :** ⭐ex: 9.3 | 1 685 545 Votes")
    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("SYNOPSIS")
    st.write("Exemple : Jake Sully, un ancien marine paraplégique, se rend sur Pandora pour participer au programme Avatar et découvre un monde fascinant et dangereux…")