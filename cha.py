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
# 3. CSS global
# ==========================

# URL de l'image de fond "Salle de Ciné Royal"
site_bg_url = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

st.markdown(f"""
<style>
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
    
    /* Image réglée à 6% d'opacité */
    opacity: 0.6;
    
    /* z-index -2 pour être tout au fond */
    z-index: -2;
    background-color: #000000;
}}

/* --- COUCHE 2 : LE FILTRE NOIR (Par dessus l'image) --- */
.stApp::after {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-color: #000000; /* Couleur Noire */
    
    /* Filtre noir à 80% d'opacité */
    opacity: 0.80;
    
    /* z-index -1 pour être entre l'image (-2) et le texte (0) */
    z-index: -1;
}}

/* --- TYPOGRAPHIE --- */
.stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown li, .stMarkdown span {{
    color: #FFFFFF !important;
}}
.stCaption {{
    color: #cccccc !important;
}}

/* --- CHAMPS DE SAISIE --- */
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
.hero-desc {{
    font-size: 1rem;
    color: #ddd !important;
    line-height: 1.6;
    margin-bottom: 35px;
    border-right: 4px solid #D7001D;
    padding-right: 20px;
    background: rgba(0,0,0,0.4);
    padding-top: 10px;
    padding-bottom: 10px;
}}
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
# 4. Barre de navigation cliquable + logo cliquable aligné
# ==========================
if 'page' not in st.session_state:
    st.session_state['page'] = 'Accueil'

def set_page(p):
    st.session_state['page'] = p

# Barre compacte avec logo et boutons alignés
col_logo, col_nav = st.columns([1, 4])

with col_logo:
    if logo_url:
        # Logo cliquable
        st.markdown(f"""
        <a href="#" onclick="window.location.reload();" style="display:flex; align-items:center; height:100%;">
            <img src="{logo_url}" width="85" style="vertical-align:middle;">
        </a>
        """, unsafe_allow_html=True)
    else:
        st.button("JUST CREUSE IT", on_click=set_page, args=("Accueil",))

with col_nav:
    nav_labels = ["Accueil", "Films", "Genres", "Acteurs", "Langue"]
    nav_cols = st.columns(len(nav_labels))
    for i, label in enumerate(nav_labels):
        if nav_cols[i].button(label):
            set_page(label)

st.markdown("---")

# ==========================
# 5. Section Hero
# ==========================
st.markdown(f"""
<div class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div>
        <div class="hero-desc">
            Une sélection exclusive de films recommandés à la carte.<br>
            Plongez dans l'univers du cinéma français et international.
        </div>
        <a href="#recherche" class="btn-main">Le Film Parfait à la Carte >>></a>
    </div>
</div>
""", unsafe_allow_html=True)

# ==========================
# 6. Section Recherche
# ==========================
st.markdown("<div id='recherche'></div>", unsafe_allow_html=True)
st.markdown("<br><h3 style='text-align:center; color:white;'>TROUVEZ VOTRE FILM COUP DE COEUR !</h3><br>", unsafe_allow_html=True)

# --- CSS POUR LE CHAMP DE TEXTE ---
st.markdown("""
<style>
/* Force le fond en blanc */
div[data-baseweb="input"] {
    background-color: white !important;
    border: 1px solid #ccc !important;
}
/* Force le texte saisi en noir */
div[data-baseweb="input"] input {
    color: black !important;
    -webkit-text-fill-color: black !important; /* Force la couleur sur Chrome/Safari */
    caret-color: black !important; /* Le curseur clignotant en noir */
}
</style>
""", unsafe_allow_html=True)
# ---------------------------------------------

c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.text_input("", placeholder="Rechercher par titre, acteur, genre...", label_visibility="collapsed")
    if st.button("SURPRENEZ-MOI", use_container_width=True):
        st.write("Recherche en cours...")

st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)

# ==========================
# 7. Section Recommandations Top 5 (Titre Rouge, Dimensions standardisées, Image complète)
# ==========================

# TITRE MODIFIÉ EN ROUGE
st.markdown("<h3 style='color:#D7001D; font-weight:800; text-transform:uppercase;'>Nos recommandations personnalisées (Top 5)</h3>", unsafe_allow_html=True)
st.markdown("<hr style='border-color:#D7001D; margin-top:0;'>", unsafe_allow_html=True)

col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)

# Données exemples
films_recommandes = [
    {"titre": "Les Évadés", "annee": "1994", "note": "9.3", "genre": "Drame", "image": os.path.join(ASSETS, "pirates2.jpg")},
    {"titre": "Forrest Gump", "annee": "1994", "note": "8.8", "genre": "Sentimental", "image": os.path.join(ASSETS, "jedi.jpg")},
    {"titre": "Le Prestige", "annee": "2006", "note": "8.5", "genre": "Thriller", "image": os.path.join(ASSETS, "pirates3.jpg")},
    {"titre": "Avatar", "annee": "2009", "note": "7.9", "genre": "Sci-Fi", "image": os.path.join(ASSETS, "avatar.jpg")},
    {"titre": "Justice League", "annee": "2021", "note": "8.1", "genre": "Action", "image": os.path.join(ASSETS, "justice_league.jpg")},
]

cols_r = [col_r1, col_r2, col_r3, col_r4, col_r5]

def afficher_carte_html(col, film):
    img_b64 = load_base64(film['image'])
    # Image par défaut si le fichier n'existe pas
    img_src = f"data:image/jpeg;base64,{img_b64}" if img_b64 else "https://via.placeholder.com/300x450/cccccc/000000?text=Image+Non+Trouvée"
    
    # MODIFICATION :
    # 1. Le conteneur <div> fixe la taille (hauteur 350px) et a un fond gris clair (#eeeeee).
    # 2. L'<img> utilise "object-fit: contain" pour que l'image soit entièrement visible.
    # 3. Ajout de <br> pour mettre le genre à la ligne.
    html_card = f"""
    <div class="movie-card">
        <div style="width: 100%; height: 350px; background-color: #eeeeee; border-radius: 4px; overflow: hidden; display: flex; align-items: center; justify-content: center;">
            <img src="{img_src}" class="movie-img" style="width: 100%; height: 100%; object-fit: contain;">
        </div>
        <h4>{film['titre']}</h4>
        <span>⭐ {film['note']} | {film['annee']}</span>
        <br>
        <span class="genre-tag">Recommandé pour {film['genre']}</span>
    </div>
    """
    with col:
        st.markdown(html_card, unsafe_allow_html=True)

for col, film in zip(cols_r, films_recommandes):
    afficher_carte_html(col, film)

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
    # MODIFICATION : 
    # 1. Container de 300px de haut (comme la vidéo).
    # 2. Fond noir pour combler les espaces vides si l'image est étroite.
    # 3. 'object-fit: contain' pour que toute l'image soit visible sans coupure.
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