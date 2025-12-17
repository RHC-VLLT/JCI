import pandas as pd
import numpy as np
import streamlit as st
import ast
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings 
import os 
import base64 

# Désactiver les warnings de Pandas/NumPy pour une meilleure lisibilité dans Streamlit
warnings.filterwarnings('ignore', category=FutureWarning)

# Définition de la valeur par défaut du selectbox
DEFAULT_SELECT_OPTION = "🎬 Tapez le nom d'un film"

# ==========================
# 1. PATHS ET CONFIGURATION
# ==========================
# Mise à jour des chemins pour les images
LOGO_PATH = os.path.join( "../assets/Logo_JCI_1.png")
BG_PATH = os.path.join("../assets/Acceuil_Pic_1_Page_1.jpg")

# URL de base pour les posters TMDB (utilisé dans la Section 7)
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"

def load_base64(path):
    """Charge une image et la convertit en base64 pour intégration CSS/HTML."""
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = load_base64(LOGO_PATH)
bg_b64 = load_base64(BG_PATH)

logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
bg_url = f"data:image/jpeg;base64,{bg_b64}" if bg_b64 else ""


st.set_page_config(
    layout="wide", 
    page_title="Just Creuse It | Recommandation de films"
)

site_bg_url = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

st.markdown(f"""
<style>
/* --- NOUVEAU NAVBAR STYLING (Moderne et Centrée) --- */
.modern-navbar-container {{
    display: flex;
    justify-content: center; 
    align-items: center;
    height: 100%;
    margin-top: 0.5%; 
}}
.modern-navbar-container a {{
    color: #FFFFFF;
    margin: 0 1%; 
    padding: 10px 10%; 
    text-decoration: none;
    font-size: 1.8rem; 
    font-weight: 700; 
    transition: all 0.3s;
    border-radius: 4px;
}}
.modern-navbar-container a:hover {{
    background-color: rgba(215, 0, 29, 0.2);
    color: #D7001D;
}}
.modern-navbar-container a.active {{
    color: #D7001D;
    border-bottom: 3px solid #D7001D; 
}}
/* --- Fin du nouveau NAVBAR STYLING --- */

/* NOUVEAU STYLE POUR AGRANDIR ET ALIGNER LE LOGO TEXTE DE SECOURS */
.logo-text-backup {{
    color: #D7001D; 
    font-size: 3.5vw; 
    font-weight: 800; 
    line-height: 1.1; 
    text-transform: uppercase;
}}

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
/* Modification du titre des films recommandés */
.film-title-display {{
    font-size: 1.1em; 
    color: white; 
    margin-top: 5px; 
    margin-bottom: 5px;
}}
/* *** CORRECTION D'ALIGNEMENT SELECTBOXES *** */
/* Cible le sélecteur N Recos dans la colonne 1 du conteneur de recherche */
div[data-testid="stVerticalBlock"] > div:nth-child(1) [data-testid="stSelectbox"] {
    /* Déplace le sélecteur N Recos vers le haut pour l'aligner avec l'autre selectbox */
    margin-top: -30px !important; 
}
/* Fin des styles */

header {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==================== 2. FONCTIONS UTILITAIRES & ML ====================

def extract_keywords(raw):
    """Transforme la chaîne JSON de TMDB en mots-clés lisibles."""
    if pd.isna(raw) or raw == "":
        return ""
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, list):
            names = [d.get("name", "").replace(" ", "") for d in data if isinstance(d, dict)]
            return " ".join(names)
        return str(raw)
    except Exception:
        return str(raw)

def build_text_features(row):
    """Construit les features textuelles séparées pour le modèle."""
    kw = extract_keywords(row.get("keywords", ""))
    keywords = kw if kw.strip() else ""
    overview = str(row.get("movie_overview_fr", row.get("movie_overview", "")))
    genres = str(row.get("movie_genres_y", "")).strip()
    return keywords, overview, genres

@st.cache_data
def load_data():
    """Charge et prépare les données brutes."""
    try:
        df_movie = pd.read_csv("../data/movie.csv")
        text_cols = ["keywords", "movie_overview_fr", "movie_overview",
                     "movie_tagline_fr", "movie_genres_y", "movie_original_title",
                     "movie_poster_url_fr", "title", "movie_poster_url"] 
        for col in text_cols:
            if col in df_movie.columns:
                df_movie[col] = df_movie[col].fillna("")
        numeric_cols = ["movie_vote_average_tmdb", "movie_popularity", 
                         "movie_startYear", "movie_runtimeMinutes"]
        for col in numeric_cols:
            if col in df_movie.columns:
                df_movie[col] = pd.to_numeric(df_movie[col], errors='coerce').fillna(0)
        
        text_features = df_movie.apply(build_text_features, axis=1, result_type='expand')
        df_movie["keywords_text"] = text_features[0]
        df_movie["overview_text"] = text_features[1]
        df_movie["genres_text"] = text_features[2]
        
        df_people = pd.read_csv("../data/intervenants.csv").rename(columns={
            "intervenant_primaryName": "person_name",
            "intervenant_primaryProfession": "person_professions",
            "intervenant_birthYear": "person_birthYear",
            "intervenant_deathYear": "person_deathYear",
        })
        df_link = pd.read_csv("../data/intermediaire.csv") 
        
        # Colonne de titre d'affichage utilisée pour le selectbox et la recherche
        df_movie['display_title'] = df_movie.apply(
            lambda row: row['title'] if row['title'] else row['movie_original_title'], axis=1
        )
        df_movie = df_movie[df_movie['display_title'] != ""].drop_duplicates(subset=['display_title'])
        
        return df_movie, df_people, df_link
    
    except FileNotFoundError as e:
        st.error(f"❌ Fichier de données non trouvé : **{e.filename}**. Assurez-vous d'avoir les fichiers nécessaires.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        st.stop()

@st.cache_resource
def build_advanced_recommender(df_movie):
    """Construit uniquement les matrices Keywords et Genres."""
    try:
        tfidf_keywords = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
        keywords_matrix = tfidf_keywords.fit_transform(df_movie["keywords_text"])
        
        tfidf_genres = TfidfVectorizer(max_features=50)
        genres_matrix = tfidf_genres.fit_transform(df_movie["genres_text"])
        
        overview_matrix = np.zeros((len(df_movie), 1))
        numeric_features = np.zeros((len(df_movie), 1))
        
        return {
            "keywords_matrix": keywords_matrix,
            "overview_matrix": overview_matrix, 
            "genres_matrix": genres_matrix,
            "numeric_features": numeric_features, 
        }
    except Exception as e:
        st.error(f"❌ Erreur lors de la construction du modèle de recommandation: {e}")
        st.stop()

def recommend_movies_hybrid(movie_title, df_movie, recommender_data, 
                            weight_keywords, weight_overview,
                            weight_genres, weight_numeric,
                            n_recommendations=5):
    """Calcule et renvoie les recommandations. movie_title est le titre D'AFFICHAGE."""
    
    matches = df_movie[df_movie["display_title"].str.lower() == movie_title.lower()]
    
    if matches.empty:
        return None, f"Film non trouvé : '{movie_title}'. Veuillez vérifier l'orthographe."
    
    movie_idx = matches.index[0]
    
    sim_keywords = cosine_similarity(recommender_data["keywords_matrix"][movie_idx], recommender_data["keywords_matrix"])[0]
    sim_genres = cosine_similarity(recommender_data["genres_matrix"][movie_idx], recommender_data["genres_matrix"])[0]
    
    sim_overview = np.zeros(len(df_movie))
    sim_numeric = np.zeros(len(df_movie))
    
    hybrid_score = (
        weight_keywords * sim_keywords +
        weight_overview * sim_overview +  
        weight_genres * sim_genres +
        weight_numeric * sim_numeric      
    )
    
    similar_indices = np.argsort(hybrid_score)[::-1]
    similar_indices_final = [idx for idx in similar_indices if idx != movie_idx][:n_recommendations]
    
    recommendations = []
    for idx in similar_indices_final:
        movie_data = df_movie.iloc[idx]
        recommendations.append({
            "titre": movie_data["display_title"],
            "tconst": movie_data["tconst"],
            "score_sim": hybrid_score[idx] * 100,
            "annee": int(movie_data.get("movie_startYear", 0)),
            "pays": movie_data.get("movie_country_y", "N/A"),
            "genres": movie_data.get("movie_genres_y", "N/A"),
            "poster_path": movie_data.get("movie_poster_url_fr", movie_data.get("movie_poster_url", "")),
            "overview": movie_data.get("movie_overview_fr", movie_data.get("movie_overview", "")),
        })
    
    return recommendations, None

# ==================== DÉBUT DU FLUX PRINCIPAL ====================

# Chargement
with st.spinner("🔄 Chargement et préparation du modèle..."):
    df_movie, df_people, df_link = load_data() 
    recommender_data = build_advanced_recommender(df_movie)

# Initialisation des variables d'état pour la session
if 'recommended_films' not in st.session_state:
    st.session_state['recommended_films'] = None
    st.session_state['recommendation_error'] = None
    st.session_state['last_search_title'] = ""
    st.session_state['detail_tconst'] = None
    st.session_state['n_recos'] = 5

# --- 4. BARRE DE NAVIGATION HTML (Logo + Liens Centrés) ---
col_logo, col_nav_center, col_spacer = st.columns([1, 3, 1])

# --- Colonne 1 : Logo ---
with col_logo:
    if logo_url:
        st.markdown(f"""
        <div style="display:flex; align-items:center; height:100%; padding-left: 2%;">
            <a href="#" onclick="window.location.reload();" style="display:block;">
                <img src="{logo_url}" width="70%" style="vertical-align:middle;"> 
            </a>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="display:flex; align-items:center; height:100%; padding-left: 2%;">
            <div class="logo-text-backup">
                JUST CREUSE IT
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Colonne 2 : Liens Centrés ---
with col_nav_center:
    st.markdown("""
    <div class="modern-navbar-container">
        <a href="#" class="active">Accueil</a>
        <a href="#">Films</a>
        <a href="#">Genre</a>
        <a href="#">Acteurs</a>
    </div>
    """, unsafe_allow_html=True)

# --- Colonne 3 : Icône Utilisateur ---
with col_spacer:
    st.markdown("""
    <div style="display:flex; justify-content:flex-end; align-items:center; height:100%; padding-right:2%;">
        <a href="#" style="color:white; font-size:1.8rem; text-decoration:none;">👤</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---") # Garder la ligne séparatrice pour l'esthétique

# --- 5. Section Hero ---
st.markdown(f"""
<div class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content">
        <div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div>
        <a href="#recherche" class="btn-main">Le Film Parfait à la Carte >>></a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- 6. Section Recherche (INTEGRATION ML TRÈS SIMPLIFIÉE AVEC ALIGNEMENT) ---
st.markdown("<div id='recherche'></div>", unsafe_allow_html=True)
st.markdown("<br><h3 style='text-align:center; color:white;'>TROUVEZ VOTRE FILM COUP DE COEUR !</h3><br>", unsafe_allow_html=True)

with st.container():
    
    # Structure des colonnes: N Recos (1.5) | Selectbox (7.5) -> Meilleur équilibre
    col_reco, col_search_select = st.columns([1.5, 7.5])
    
    # 1. PARAMÈTRES FIXES ET N RECOS
    
    # Fixation des poids (50/50 pour Style et Genre)
    weight_keywords_raw = 1.0 
    weight_genres_raw = 1.0 
    
    # Calcul des poids normalisés (résultat: 0.5 pour KW, 0.5 pour Genre)
    total_weight = weight_keywords_raw + weight_genres_raw
    weight_keywords = weight_keywords_raw / total_weight # 0.5
    weight_genres = weight_genres_raw / total_weight     # 0.5
    weight_overview = 0.0
    weight_numeric = 0.0

    # Stocker les poids pour la fonction de recommandation
    st.session_state['weight_keywords'] = weight_keywords
    st.session_state['weight_genres'] = weight_genres

    options_reco = [3, 5, 10] # Nouvelle liste d'options
    default_index = options_reco.index(st.session_state.get('n_recos', 5)) # Trouve l'index par défaut
    
    with col_reco:
        # NOTE: Le CSS gère l'alignement vertical
        n_recos = st.selectbox(
            "N Recos", 
            options_reco, 
            index=default_index, 
            key="select_nrecos", 
            help="Nombre de films recommandés à afficher", 
            label_visibility="collapsed"
        )
        st.session_state['n_recos'] = n_recos

    # 2. SELECTBOX DE RECHERCHE AVEC AUTO-COMPLÉTION
    with col_search_select:
        movie_titles_for_selectbox = [DEFAULT_SELECT_OPTION] + sorted(df_movie['display_title'].unique().tolist())
        
        selected_movie_title_display = st.selectbox(
            label="Barre de recherche (Tapez pour Filtrer)",
            options=movie_titles_for_selectbox,
            index=0,
            placeholder=DEFAULT_SELECT_OPTION,
            label_visibility="collapsed",
            key="simple_movie_selector"
        )

    # 3. LOGIQUE DE DÉCLENCHEMENT
    search_submitted = False
    if selected_movie_title_display and selected_movie_title_display != DEFAULT_SELECT_OPTION:
        search_submitted = True
        search_title = selected_movie_title_display.strip()
        
        if search_submitted:
            with st.spinner(f"Recherche des recommandations pour **{search_title}**..."):
                recommended_films, recommendation_error = recommend_movies_hybrid(
                    search_title,
                    df_movie,
                    recommender_data,
                    weight_keywords=weight_keywords,
                    weight_overview=weight_overview,
                    weight_genres=weight_genres,
                    weight_numeric=weight_numeric,
                    n_recommendations=st.session_state['n_recos'] 
                )
                
                # Stocke le résultat dans l'état de session
                st.session_state['recommended_films'] = recommended_films
                st.session_state['recommendation_error'] = recommendation_error
                st.session_state['last_search_title'] = search_title

    # Affichage des erreurs si elles existent après la tentative de recherche
    if st.session_state.get('recommendation_error'):
        st.error(st.session_state['recommendation_error'])

st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)

# --- 7. Section Recommandations Top N (Dynamique) ---

recommended_films = st.session_state.get('recommended_films')
search_title = st.session_state.get('last_search_title', "")

if recommended_films:
    st.markdown(f"<h1 style='text-align: center; color:#D7001D;'> Top {len(recommended_films)} films similaires à **{search_title}** </h1>", unsafe_allow_html=True)
    st.write("---")
    
    # Utilise st.columns pour l'affichage en grille
    cols = st.columns(len(recommended_films))
    
    for i, film in enumerate(recommended_films):
        with cols[i]:
            st.markdown(f"**<h3 style='color:#D7001D; text-align:center;'>#{i+1}</h3>**", unsafe_allow_html=True)
            
            poster_url = POSTER_BASE_URL + film["poster_path"] if film["poster_path"] and film["poster_path"].startswith("/") else film["poster_path"]
            
            if poster_url and film["poster_path"]:
                st.image(poster_url, use_container_width=True)
            else:
                st.markdown(f"<div style='height:250px; background-color:#333; display:flex; align-items:center; justify-content:center; border-radius:5px;'>Image non disponible</div>", unsafe_allow_html=True)
                
            # Affichage du titre en gras
            title_html = f"<b>{film['titre']}</b>"
            st.markdown(f"<div class='film-title-display' style='text-align:center;'>{title_html}</div>", unsafe_allow_html=True)

            st.markdown(f"<p style='text-align:center; margin-top:0;'>Score: {film['score_sim']:.1f}%</p>", unsafe_allow_html=True)
            
            st.write(f"**{film['annee']}** | {film['pays']}")
            st.write(f"*{film['genres']}*")
            
            # Bouton de détails (sans fonctionnalité complète ici)
            st.button("Voir détails du film", key=f"details_{film['tconst']}_{i}") 
            
else:
    # Affichage par défaut si aucune recommandation n'a été faite
    st.markdown("<h1 style='text-align: center; color:#D7001D;'> Entrez le titre d'un film pour commencer la recommandation ! </h1>", unsafe_allow_html=True)
    st.write("---")


st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("🤖 IA basée sur le contenu: TF-IDF (Keywords, Genres) + Sim. Cosinus Pondérée | © 2025")