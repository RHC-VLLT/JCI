import streamlit as st
import os
import base64
import ast
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

LOGO_PATH = os.path.join( "../assets/Logo_JCI_1.png")
BG_PATH = os.path.join("../assets/Acceuil_Pic_1_Page_1.jpg")

# URL de base pour les posters TMDB (utilisé dans la Section 7)
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"
DEFAULT_SELECT_OPTION = "Tapez le nom d'un film"

def load_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = load_base64(LOGO_PATH)
bg_b64 = load_base64(BG_PATH)

logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
bg_url = f"data:image/jpeg;base64,{bg_b64}" if bg_b64 else ""


# ==================== 0. FONCTIONS UTILITAIRES & ML ====================

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
        
        # Ajout d'une colonne de mapping pour faciliter la recherche inverse
        df_movie['display_title'] = df_movie.apply(
            lambda row: row['title'] if row['title'] else row['movie_original_title'], axis=1
        )
        df_movie = df_movie[df_movie['display_title'] != ""].drop_duplicates(subset=['display_title'])
        
        return df_movie, df_people, df_link
    
    except FileNotFoundError as e:
        st.error(f" Fichier de données non trouvé : **{e.filename}**. Assurez-vous d'avoir les fichiers nécessaires.")
        st.stop()
    except Exception as e:
        st.error(f" Erreur lors du chargement des données: {e}")
        st.stop()

@st.cache_resource
def build_advanced_recommender(df_movie):
    """Construit uniquement les matrices Keywords et Genres."""
    try:
        tfidf_keywords = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
        keywords_matrix = tfidf_keywords.fit_transform(df_movie["keywords_text"])
        
        tfidf_genres = TfidfVectorizer(max_features=50)
        genres_matrix = tfidf_genres.fit_transform(df_movie["genres_text"])
        
        # Placeholder pour les matrices non utilisées dans cette version (Overview/Numeric)
        overview_matrix = np.zeros((len(df_movie), 1)) 
        numeric_features = np.zeros((len(df_movie), 1))
        
        return {
            "keywords_matrix": keywords_matrix,
            "overview_matrix": overview_matrix, 
            "genres_matrix": genres_matrix,
            "numeric_features": numeric_features, 
        }
    except Exception as e:
        st.error(f" Erreur lors de la construction du modèle de recommandation: {e}")
        st.stop()

def recommend_movies_hybrid(movie_title, df_movie, recommender_data, 
                           weight_keywords, weight_overview,
                           weight_genres, weight_numeric,
                           n_recommendations=5):
    """Calcule et renvoie les recommandations."""
    
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


header {{visibility: hidden;}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)


# ==================== CHARGEMENT ET INITIALISATION DU ML ====================

# Chargement des données et construction du modèle (Exécuté une seule fois grâce au cache)
df_movie, df_people, df_link = load_data()
recommender_data = build_advanced_recommender(df_movie)

# Initialisation des variables d'état pour la session
if 'recommended_films' not in st.session_state:
    st.session_state['recommended_films'] = None
    st.session_state['recommendation_error'] = None
    st.session_state['last_search_title'] = ""
    st.session_state['detail_tconst'] = None
    # Paramètres par défaut des poids (ajustables par les sliders)
    st.session_state['weight_keywords'] = 0.5
    st.session_state['weight_genres'] = 0.5
    st.session_state['weight_overview'] = 0.0
    st.session_state['weight_numeric'] = 0.0
    st.session_state['n_recos'] = 5


# ==========================
# 4. BARRE DE NAVIGATION HTML (Logo + Liens Centrés)
# ==========================

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



# =========================================================
# 6. SECTION RECHERCHE (PARAMÈTRES FIXÉS)
# =========================================================
st.markdown("<div id='recherche'></div>", unsafe_allow_html=True)

st.markdown("""
    <div style='text-align:center; margin-top: 50px; margin-bottom: 20px;'>
        <h1 style='color:white; font-weight:800; font-size: 2.8rem; letter-spacing:-1.5px;'>
            TROUVEZ VOTRE FILM COUP DE COEUR !
        </h1>
    </div>
""", unsafe_allow_html=True)

# CSS pour la barre de recherche (Pilule)
st.markdown("""<style>
    div[data-baseweb="select"] { border-radius: 50px !important; background-color: #111 !important; border: 2px solid #333 !important; padding: 5px 20px !important; }
    div[data-baseweb="select"]:focus-within { border-color: #D7001D !important; box-shadow: 0 0 20px rgba(215, 0, 29, 0.4) !important; }
</style>""", unsafe_allow_html=True)

# LIGNE 1 : BARRE DE RECHERCHE
with st.container():
    movie_titles = sorted(df_movie['display_title'].unique().tolist())
    selected_movie = st.selectbox(
        label="Recherche de film",
        options=movie_titles,
        index=None, 
        placeholder="Tapez le nom d'un film pour obtenir des recommandations instantanées...",
        label_visibility="collapsed",
        key="simple_movie_selector"
    )

# Logique de recommandation (Poids fixés : KW 0.35, Genre 1.00)
w_kw_raw, w_ge_raw = 0.35, 1.00
total_w = w_kw_raw + w_ge_raw
w_kw_norm, w_ge_norm = w_kw_raw / total_w, w_ge_raw / total_w
w_ov, w_nu = 0.0, 0.0
n_recos = 30 # Augmenter le pool pour avoir plus de 5 films > 50%

search_title = selected_movie.strip() if selected_movie else None
if search_title and (search_title != st.session_state.get('last_search_title')):
    with st.spinner(f"Analyse de l'ADN du film **{search_title}**..."):
        recommended_films, _ = recommend_movies_hybrid(
            search_title, df_movie, recommender_data,
            weight_keywords=w_kw_norm, weight_overview=w_ov,
            weight_genres=w_ge_norm, weight_numeric=w_nu,
            n_recommendations=n_recos 
        )
        st.session_state['recommended_films'] = recommended_films
        st.session_state['last_search_title'] = search_title

st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)

# =========================================================
# 7. SECTION CARROUSEL LOOP (TOP 5 PUIS LE RESTE > 50%)
# =========================================================
all_recos = st.session_state.get('recommended_films')
# 1. Filtrage strict : score > 50.0%
filtered_recos = [f for f in all_recos if f.get('score_sim', 0) > 50.0] if all_recos else []

# 2. Séquencement : TOP 5 puis LE RESTE
top_5 = filtered_recos[:5]
the_rest = filtered_recos[5:]
carousel_films = top_5 + the_rest # La liste séquencée complète

if carousel_films:
    st.markdown(f"<h2 style='text-align:center;color:white;font-weight:800;margin:40px 0;'>NOTRE SÉLECTION POUR VOUS ({len(carousel_films)} FILMS)</h2>", unsafe_allow_html=True)
    
    # CSS de l'animation Loop (Calcul dynamique)
    n_films_total = len(carousel_films)
    card_width = 380
    gap = 25
    track_width = (card_width + gap) * n_films_total # Largeur de la liste unique
    
    st.markdown("""<style>
        /* Styles conservés de vos cartes */
        .movie-card-xl { flex: 0 0 """ + str(card_width) + """px; margin: 0 """ + str(gap / 2) + """px; background-color: #0a0a0a; border: 1px solid #222; border-radius: 15px; height: 750px; position: relative; overflow: hidden; transition: all 0.4s ease; }
        .movie-card-xl:hover { transform: translateY(-5px); border-color: #D7001D !important; }
        .movie-card-xl:hover .btn-html-red { background-color: #FFFFFF !important; color: #D7001D !important; letter-spacing: 2px !important;}
        .card-red-btn { position:absolute; bottom:0; left:0; width:100%; height:60px; background-color:#D7001D; color:white; display:flex; align-items:center; justify-content:center; font-weight:900; text-transform:uppercase; letter-spacing:1px; transition:0.3s;}
        
        /* Styles du Carrousel */
        .carousel-viewport { width: 100%; overflow: hidden; position: relative; padding: 20px 0; }
        .carousel-track {
            display: flex;
            width: calc(""" + str((card_width + gap) * (n_films_total * 2)) + """px);
            animation: scroll """ + str(n_films_total * 5) + """s linear infinite; /* Vitesse: 5s par film */
        }
        .carousel-track:hover { animation-play-state: paused; }
        @keyframes scroll {
            0% { transform: translateX(0); }
            100% { transform: translateX(calc(-""" + str(track_width) + """px)); }
        }

        /* FIX : Bouton Streamlit invisible pour le clic stable (conserve l'UX) */
        div.stButton > button { position: absolute !important; bottom: 0px !important; left: 0px !important; width: 100% !important; height: 60px !important; background: transparent !important; color: transparent !important; border: none !important; z-index: 1000 !important; margin: 0 !important; cursor: pointer !important; }
    </style>""", unsafe_allow_html=True)

    # --- Rendu de la piste Carrousel ---
    items_html = ""
    # On itère deux fois sur la liste séquencée (Top 5 + Reste) pour la boucle
    for film_list in [carousel_films, carousel_films]:
        for film in film_list:
            pst = POSTER_BASE_URL + str(film["poster_path"]) if film.get("poster_path") else ""
            scr = f"{film['score_sim']:.1f}%"
            tit = str(film.get('titre', 'SANS TITRE')).upper()
            inf = f"{film.get('annee', '')} • {str(film.get('genres', '')).split(',')[0].upper()}"

            # Injection du HTML de la carte (Basé sur votre style XL)
            card_html = f'''
            <div class="movie-card-xl">
                <div style="position:relative;height:550px;width:100%;overflow:hidden;">
                    <div style="position:absolute;top:20px;right:20px;background:#D7001D;color:white;padding:5px 15px;border-radius:6px;font-size:1rem;font-weight:900;z-index:5;">{scr}</div>
                    <img src="{pst}" style="width:100%;height:100%;object-fit:cover;display:block;">
                    <div style="position:absolute;bottom:0;left:0;width:100%;height:50%;background:linear-gradient(to top,#0a0a0a,transparent);"></div>
                </div>
                <div style="padding:20px;text-align:center;">
                    <div style="color:white;font-weight:800;font-size:1.1rem;margin-bottom:8px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{tit}</div>
                    <div style="color:#D7001D;font-size:0.9rem;font-weight:700;">{inf}</div>
                </div>
                <div class="card-red-btn btn-html-red">Voir détails</div>
            </div>'''
            items_html += card_html

    st.markdown(f'<div class="carousel-viewport"><div class="carousel-track">{items_html}</div></div>', unsafe_allow_html=True)
    
    # Gestion des clics avec st.columns + st.button invisible (pour l'interaction stable)
    # Créer le même nombre de colonnes que de cartes visibles à l'écran, et y mettre les boutons invisibles
    # pour capturer le clic sans créer de barre de recherche.
    
    # Nous utilisons la technique des colonnes cachées juste pour l'injection des boutons
    cols = st.columns(n_films_total)
    
    for i, film in enumerate(carousel_films):
        with cols[i]:
            # Injecte un bouton invisible/transparent au-dessus de chaque carte pour le clic
            if st.button(" ", key=f"btn_car_{film['tconst']}_{i}"):
                st.session_state['detail_tconst'] = film['tconst']
                st.rerun()

# =========================================================
# 8. Section Détails (STYLE CONSERVÉ & SANS FINANCE)
# =========================================================
detail_id = st.session_state.get('detail_tconst')

if detail_id:
    m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
    
    # Récupération des données
    ids_p = df_link[df_link['tconst'] == detail_id]['nconst'].tolist()
    peoples = df_people[df_people['nconst'].isin(ids_p)]
    reals = peoples[peoples['person_professions'].str.contains('director', na=False)]['person_name'].tolist()
    acts = peoples[peoples['person_professions'].str.contains('actor|actress', na=False)]['person_name'].head(5).tolist()

    pst_det = POSTER_BASE_URL + str(m["movie_poster_url_fr"]) if m["movie_poster_url_fr"] else ""
    synop = str(m['movie_overview_fr'] if m['movie_overview_fr'] else m['movie_overview']).replace('"', '&quot;')
    
    # Stats, Origine et Trailer
    pop = m.get("movie_popularity", 0)
    vote = m.get("movie_vote_average_tmdb", 0)
    stats_box = f'<div style="margin-top:20px;background:rgba(255,255,255,0.05);padding:15px;border-radius:15px;border:1px solid rgba(255,255,255,0.1);"><p style="color:#888;font-size:0.7rem;text-transform:uppercase;margin:0;">Popularité / Note</p><p style="color:white;font-weight:800;font-size:1.1rem;margin:0;">📈 {pop} | ⭐ {vote}/10</p></div>' if pop or vote else ""
    
    country = m.get("production_1_countries_name")
    country_html = f'<div style="padding:20px;background:rgba(215,0,29,0.05);border-radius:15px;border:1px solid rgba(215,0,29,0.1);"><h4 style="color:#D7001D;font-size:0.75rem;text-transform:uppercase;">Origine</h4><p style="color:white;font-weight:600;">{country}</p></div>' if pd.notna(country) else ""

    tr_url = m.get('trailer_url_fr', m.get('youtube_url', ""))
    tr_btn = f'<a href="{tr_url}" target="_blank" style="text-decoration:none;"><div style="display:inline-flex;align-items:center;background-color:#D7001D;color:white;padding:12px 25px;border-radius:50px;font-weight:700;font-size:0.9rem;margin-top:20px;cursor:pointer;box-shadow:0 4px 15px rgba(215,0,29,0.3);text-transform:uppercase;letter-spacing:1px;"><span style="margin-right:10px;">▶</span> Voir la bande-annonce</div></a>' if pd.notna(tr_url) and "http" in str(tr_url) else ""


    # Rendu final
    detail_html = f'''<div style="background-color:#050505;border-radius:25px;border:1px solid #333;overflow:hidden;display:flex;flex-wrap:wrap;min-height:550px;position:relative;"><div style="position:absolute;top:0;left:0;width:100%;height:100%;background-image:url(\'{pst_det}\');background-size:cover;background-position:center;filter:blur(50px) brightness(0.2);z-index:1;"></div><div style="position:relative;z-index:2;display:flex;width:100%;padding:50px;gap:40px;flex-wrap:wrap;"><div style="flex:1;min-width:300px;max-width:350px;"><img src="{pst_det}" style="width:100%;border-radius:15px;box-shadow:0 15px 40px rgba(0,0,0,0.8);">{stats_box}</div><div style="flex:2;min-width:400px;display:flex;flex-direction:column;justify-content:center;"><h1 style="color:white;font-weight:900;font-size:3rem;margin:0;">{str(m["title"]).upper()}</h1><p style="color:#D7001D;font-weight:700;font-size:1.2rem;margin-top:15px;">{m["movie_startYear"]} • {m["movie_runtimeMinutes"]} MIN • {str(m["movie_genres_y"]).upper()}</p><div style="margin:25px 0;border-left:4px solid #D7001D;padding-left:20px;"><p style="color:#EEE;font-size:1.1rem;line-height:1.6;font-style:italic;">"{synop}"</p></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:20px;"><div><h4 style="color:#666;font-size:0.75rem;text-transform:uppercase;">Réalisation</h4><p style="color:white;font-weight:600;">{", ".join(reals) if reals else "N/A"}</p></div><div><h4 style="color:#666;font-size:0.75rem;text-transform:uppercase;">Casting</h4><p style="color:white;font-weight:600;">{", ".join(acts) if acts else "N/A"}</p></div></div>{country_html}{tr_btn}</div></div></div>'''

    st.markdown(detail_html, unsafe_allow_html=True)
    if st.button("⬅ RETOUR À LA SÉLECTION", use_container_width=True):
        st.session_state['detail_tconst'] = None
        st.rerun()