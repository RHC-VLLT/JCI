# ==============================================================================
# 1. IMPORTS ET CONFIGURATION
# ==============================================================================
import os
import ast
import base64
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(
    page_title="Just Creuse It - Cinéma",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# 2. CONSTANTES GLOBALES
# ==============================================================================
LOGO_PATH = "../assets/Logo_JCI_1.png"
BG_PATH = "../assets/Acceuil_Pic_1_Page_1.jpg"
SITE_BG_URL = "https://images.unsplash.com/photo-1517604931442-7e0c8ed2963c?q=80&w=2070&auto=format&fit=crop"

WEIGHT_KEYWORDS = 0.35
WEIGHT_GENRES = 1.00
N_RECOMMENDATIONS = 30
CARDS_PER_ROW_TOP5 = 5
CARDS_PER_ROW_ALL = 4

# ==============================================================================
# 3. FONCTIONS UTILITAIRES
# ==============================================================================
def load_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def extract_keywords(raw):
    if pd.isna(raw) or raw == "":
        return ""
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, list):
            return " ".join([d.get("name", "").replace(" ", "") for d in data if isinstance(d, dict)])
        return str(raw)
    except:
        return str(raw)

def build_text_features(row):
    kw = extract_keywords(row.get("keywords", ""))
    keywords = kw if kw.strip() else ""
    overview = str(row.get("movie_overview_fr", row.get("movie_overview", "")))
    genres = str(row.get("movie_genres_y", "")).strip()
    return keywords, overview, genres

def get_poster_url(row):
    if pd.notna(row.get("movie_poster_url_fr")) and row.get("movie_poster_url_fr"):
        return str(row["movie_poster_url_fr"])
    elif pd.notna(row.get("movie_poster_path_fr")) and row.get("movie_poster_path_fr"):
        return f"https://image.tmdb.org/t/p/w500{row['movie_poster_path_fr']}"
    elif pd.notna(row.get("movie_poster_path_1")) and row.get("movie_poster_path_1"):
        return f"https://image.tmdb.org/t/p/w500{row['movie_poster_path_1']}"
    return ""

# ==============================================================================
# 4. CHARGEMENT DES DONNEES
# ==============================================================================
@st.cache_data
def load_data():
    try:
        df_movie = pd.read_csv("../data/movie.csv")
        
        text_cols = ["keywords", "movie_overview_fr", "movie_overview", "movie_tagline_fr", 
                     "movie_genres_y", "movie_original_title", "movie_poster_url_fr", "title", 
                     "movie_poster_path_fr", "movie_poster_path_1"]
        for col in text_cols:
            if col in df_movie.columns:
                df_movie[col] = df_movie[col].fillna("")
        
        numeric_cols = ["movie_vote_average_tmdb", "movie_popularity", "movie_startYear", "movie_runtimeMinutes"]
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
        
        df_movie['display_title'] = df_movie.apply(
            lambda row: row['title'] if row['title'] else row['movie_original_title'], axis=1
        )
        df_movie = df_movie[df_movie['display_title'] != ""].drop_duplicates(subset=['display_title'])
        
        return df_movie, df_people, df_link
    except FileNotFoundError as e:
        st.error(f"Fichier non trouvé: {e.filename}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur: {e}")
        st.stop()

@st.cache_resource
def build_recommender(df_movie):
    try:
        tfidf_keywords = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
        keywords_matrix = tfidf_keywords.fit_transform(df_movie["keywords_text"])
        
        tfidf_genres = TfidfVectorizer(max_features=50)
        genres_matrix = tfidf_genres.fit_transform(df_movie["genres_text"])
        
        return {"keywords_matrix": keywords_matrix, "genres_matrix": genres_matrix}
    except Exception as e:
        st.error(f"Erreur modèle: {e}")
        st.stop()

def recommend_movies(movie_title, df_movie, recommender_data, n_recommendations=5):
    matches = df_movie[df_movie["display_title"].str.lower() == movie_title.lower()]
    
    if matches.empty:
        return None, f"Film non trouvé: '{movie_title}'"
    
    movie_idx = matches.index[0]
    
    sim_keywords = cosine_similarity(recommender_data["keywords_matrix"][movie_idx], 
                                    recommender_data["keywords_matrix"])[0]
    sim_genres = cosine_similarity(recommender_data["genres_matrix"][movie_idx], 
                                  recommender_data["genres_matrix"])[0]
    
    total_weight = WEIGHT_KEYWORDS + WEIGHT_GENRES
    hybrid_score = (WEIGHT_KEYWORDS / total_weight) * sim_keywords + (WEIGHT_GENRES / total_weight) * sim_genres
    
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
            "poster_url": get_poster_url(movie_data),
            "overview": movie_data.get("movie_overview_fr", movie_data.get("movie_overview", "")),
        })
    
    return recommendations, None

# ==============================================================================
# 5. CHARGEMENT DES ASSETS
# ==============================================================================
logo_b64 = load_base64(LOGO_PATH)
bg_b64 = load_base64(BG_PATH)
logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
bg_url = f"data:image/jpeg;base64,{bg_b64}" if bg_b64 else ""

# ==============================================================================
# 6. CSS GLOBAL
# ==============================================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&display=swap');

html, body, [class*="css"], .stApp {{
    font-family: 'Montserrat', sans-serif;
    color: #FFFFFF !important;
    background-color: transparent !important;
}}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-image: url('{SITE_BG_URL}');
    background-size: cover;
    background-position: center;
    opacity: 0.6;
    z-index: -2;
    background-color: #000000;
}}

.stApp::after {{
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100vw; height: 100vh;
    background-color: #000000;
    opacity: 0.80;
    z-index: -1;
}}

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

.logo-text-backup {{
    color: #D7001D;
    font-size: 3.5vw;
    font-weight: 800;
    line-height: 1.1;
    text-transform: uppercase;
}}

.stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown li, .stMarkdown span {{
    color: #FFFFFF !important;
}}

div[data-baseweb="input"], div[data-baseweb="select"] {{
    background-color: #1a1a1a !important;
    border: 1px solid #333;
    border-radius: 50px !important;
    opacity: 0.9;
}}

div[data-baseweb="input"] input, div[data-baseweb="select"] {{
    color: white !important;
}}

div[data-baseweb="select"]:focus-within {{
    border-color: #D7001D !important;
    box-shadow: 0 0 20px rgba(215, 0, 29, 0.4) !important;
}}

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

.movie-card-xl {{
    flex: 1;
    min-width: 0;
    margin: 0 5px;
    background-color: #0a0a0a;
    border: 1px solid #222;
    border-radius: 15px;
    height: 680px;
    position: relative;
    overflow: hidden;
    transition: all 0.4s ease;
}}

.movie-card-xl:hover {{
    transform: translateY(-5px);
    border-color: #D7001D !important;
}}

header, #MainMenu, footer {{visibility: hidden;}}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. INITIALISATION DES DONNEES
# ==============================================================================
df_movie, df_people, df_link = load_data()
recommender_data = build_recommender(df_movie)

if 'recommended_films' not in st.session_state:
    st.session_state['recommended_films'] = None
    st.session_state['last_search_title'] = ""
    st.session_state['detail_tconst'] = None
    st.session_state['show_all_recos'] = False

# ==============================================================================
# 8. VERIFICATION SI MODE DETAILS
# ==============================================================================
detail_id = st.session_state.get('detail_tconst')

if not detail_id:
    # ==============================================================================
    # 9. NAVIGATION
    # ==============================================================================
    col_logo, col_nav_center, col_spacer = st.columns([1, 3, 1])

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
                <div class="logo-text-backup">JUST CREUSE IT</div>
            </div>
            """, unsafe_allow_html=True)

    with col_nav_center:
        st.markdown("""
        <div class="modern-navbar-container">
            <a href="#" class="active">Accueil</a>
            <a href="#">Films</a>
            <a href="#">Genre</a>
            <a href="#">Acteurs</a>
        </div>
        """, unsafe_allow_html=True)

    with col_spacer:
        st.markdown("""
        <div style="display:flex; justify-content:flex-end; align-items:center; height:100%; padding-right:2%;">
            <a href="#" style="color:white; font-size:1.8rem; text-decoration:none;">&#128100;</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ==============================================================================
    # 10. SECTION HERO
    # ==============================================================================
    st.markdown(f"""
    <div class="hero">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div>
            <a href="#recherche" class="btn-main">Le Film Parfait à la Carte</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==============================================================================
    # 11. SECTION RECHERCHE
    # ==============================================================================
    st.markdown("<div id='recherche'></div>", unsafe_allow_html=True)
    st.markdown("""
        <div style='text-align:center; margin-top: 50px; margin-bottom: 20px;'>
            <h1 style='color:white; font-weight:800; font-size: 2.8rem; letter-spacing:-1.5px;'>
                TROUVEZ VOTRE FILM COUP DE COEUR
            </h1>
        </div>
    """, unsafe_allow_html=True)

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

    search_title = selected_movie.strip() if selected_movie else None
    if search_title and (search_title != st.session_state.get('last_search_title')):
        with st.spinner(f"Analyse de l'ADN du film {search_title}..."):
            recommended_films, _ = recommend_movies(
                search_title, df_movie, recommender_data, n_recommendations=N_RECOMMENDATIONS
            )
            st.session_state['recommended_films'] = recommended_films
            st.session_state['last_search_title'] = search_title
            st.session_state['show_all_recos'] = False

    st.markdown("<br><hr style='border-color:#333'><br>", unsafe_allow_html=True)

    # ==============================================================================
    # 12. GRILLE DE RECOMMANDATIONS
    # ==============================================================================
    all_recos = st.session_state.get('recommended_films')
    filtered_recos = [f for f in all_recos if f.get('score_sim', 0) > 50.0] if all_recos else []

    top_5 = filtered_recos[:5]

    if st.session_state.get('show_all_recos'):
        films_to_display = filtered_recos
        display_title = f"TOUS LES RESULTATS ({len(films_to_display)} FILMS)"
        cards_per_row = CARDS_PER_ROW_ALL
    else:
        films_to_display = top_5
        display_title = "TOP 5 DES RECOMMANDATIONS"
        cards_per_row = CARDS_PER_ROW_TOP5

    if films_to_display:
        st.markdown(f"<h2 style='text-align:center;color:white;font-weight:800;margin:40px 0;'>{display_title}</h2>", 
                    unsafe_allow_html=True)
        
        cols = st.columns(cards_per_row)
        
        for i, film in enumerate(films_to_display):
            with cols[i % cards_per_row]:
                poster_url = film.get("poster_url", "")
                scr = f"{film['score_sim']:.1f}%"
                tit = str(film.get('titre', 'SANS TITRE')).upper()
                inf = f"{film.get('annee', '')} • {str(film.get('genres', '')).split(',')[0].upper()}"

                card_html = f'''
                <div class="movie-card-xl" style="margin-bottom: 5px;">
                    <div style="position:relative;height:550px;width:100%;overflow:hidden;">
                        <div style="position:absolute;top:20px;right:20px;background:#D7001D;color:white;padding:5px 15px;border-radius:6px;font-size:1rem;font-weight:900;z-index:5;">{scr}</div>
                        <img src="{poster_url}" style="width:100%;height:100%;object-fit:cover;display:block;">
                        <div style="position:absolute;bottom:0;left:0;width:100%;height:50%;background:linear-gradient(to top,#0a0a0a,transparent);"></div>
                    </div>
                    <div style="padding:20px 5px;text-align:center;">
                        <div style="color:white;font-weight:800;font-size:1.1rem;margin-bottom:8px;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;">{tit}</div>
                        <div style="color:#D7001D;font-size:0.9rem;font-weight:700;">{inf}</div>
                    </div>
                </div>'''
                
                st.markdown(card_html, unsafe_allow_html=True)
                
                if st.button("VOIR DETAILS", key=f"btn_grid_{film['tconst']}_{i}", use_container_width=True):
                    st.session_state['detail_tconst'] = film['tconst']
                    st.rerun()

        if not st.session_state.get('show_all_recos') and len(filtered_recos) > 5:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"VOIR TOUTES LES {len(filtered_recos) - 5} AUTRES RECOMMANDATIONS", 
                        use_container_width=True, key="show_all_btn"):
                st.session_state['show_all_recos'] = True
                st.rerun()

else:
    # ==============================================================================
    # 13. PAGE DETAILS DU FILM
    # ==============================================================================
    
    # 13.1 Récupération des données
    m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
    
    ids_p = df_link[df_link['tconst'] == detail_id]['nconst'].tolist()
    peoples = df_people[df_people['nconst'].isin(ids_p)]
    
    reals = peoples[peoples['person_professions'].str.contains('director', na=False)]['person_name'].tolist()
    acts = peoples[peoples['person_professions'].str.contains('actor|actress', na=False)]['person_name'].head(5).tolist()

    poster_detail_url = get_poster_url(m)
    synop = str(m['movie_overview_fr'] if pd.notna(m['movie_overview_fr']) else m['movie_overview']).replace('"', '&quot;').replace("'", "&#39;")
    titre = str(m["title"]).upper().replace('"', '&quot;').replace("'", "&#39;")
    
    pop = m.get("movie_popularity", 0)
    vote = m.get("movie_vote_average_tmdb", 0)
    annee = int(m["movie_startYear"]) if pd.notna(m["movie_startYear"]) else "N/A"
    duree = int(m["movie_runtimeMinutes"]) if pd.notna(m["movie_runtimeMinutes"]) else "N/A"
    genres = str(m["movie_genres_y"]).upper() if pd.notna(m["movie_genres_y"]) else "N/A"
    
    # 13.2 Construction des blocs HTML
    if pop or vote:
        stats_block = f"""
        <div style="margin-top:20px;background:rgba(255,255,255,0.05);padding:15px;border-radius:15px;border:1px solid rgba(255,255,255,0.1);">
            <p style="color:#888;font-size:0.7rem;text-transform:uppercase;margin:0;">Popularité / Note</p>
            <p style="color:white;font-weight:800;font-size:1.1rem;margin:0;">{pop} | {vote}/10</p>
        </div>
        """
    else:
        stats_block = ""
    
    country = m.get("production_1_countries_name")
    if pd.notna(country):
        country_block = f"""
        <div style="padding:20px;background:rgba(215,0,29,0.05);border-radius:15px;border:1px solid rgba(215,0,29,0.1);">
            <h4 style="color:#D7001D;font-size:0.75rem;text-transform:uppercase;">Origine</h4>
            <p style="color:white;font-weight:600;">{country}</p>
        </div>
        """
    else:
        country_block = ""

    tr_url = m.get('trailer_url_fr', m.get('youtube_url', ""))
    if pd.notna(tr_url) and "http" in str(tr_url):
        trailer_button = f"""
        <a href="{tr_url}" target="_blank" style="text-decoration:none;">
            <div style="display:inline-flex;align-items:center;background-color:#D7001D;color:white;padding:12px 25px;border-radius:50px;font-weight:700;font-size:0.9rem;margin-top:20px;cursor:pointer;box-shadow:0 4px 15px rgba(215,0,29,0.3);text-transform:uppercase;letter-spacing:1px;">
                VOIR LA BANDE-ANNONCE
            </div>
        </a>
        """
    else:
        trailer_button = ""

    realisateurs_text = ", ".join(reals) if reals else "N/A"
    acteurs_text = ", ".join(acts) if acts else "N/A"

    # 13.3 Affichage de la carte avec fond noir semi-transparent et flouté
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="max-width:1400px;margin:0 auto;background-color:rgba(10,10,10,0.90);backdrop-filter:blur(25px);border-radius:25px;border:1px solid rgba(255,255,255,0.15);overflow:hidden;padding:50px;box-shadow:0 20px 60px rgba(0,0,0,0.9);"
    """, unsafe_allow_html=True)
    
    col_poster, col_info = st.columns([1, 2])
    
    with col_poster:
        st.markdown(f"""
        <img src="{poster_detail_url}" style="width:100%;border-radius:15px;box-shadow:0 15px 40px rgba(0,0,0,0.8);">
        {stats_block}
        """, unsafe_allow_html=True)
    
    with col_info:
        st.markdown(f"""
        <h1 style="color:white;font-weight:900;font-size:3rem;margin:0;">{titre}</h1>
        <p style="color:#D7001D;font-weight:700;font-size:1.2rem;margin-top:15px;">{annee} • {duree} MIN • {genres}</p>
        
        <div style="margin:25px 0;border-left:4px solid #D7001D;padding-left:20px;">
            <p style="color:#EEE;font-size:1.1rem;line-height:1.6;font-style:italic;">"{synop}"</p>
        </div>
        
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:30px;margin-bottom:20px;">
            <div>
                <h4 style="color:#666;font-size:0.75rem;text-transform:uppercase;">Réalisation</h4>
                <p style="color:white;font-weight:600;">{realisateurs_text}</p>
            </div>
            <div>
                <h4 style="color:#666;font-size:0.75rem;text-transform:uppercase;">Casting</h4>
                <p style="color:white;font-weight:600;">{acteurs_text}</p>
            </div>
        </div>

        
        {country_block}
        {trailer_button}
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 13.4 Bouton retour
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("RETOUR A LA SELECTION", use_container_width=True, key="btn_back_detail"):
        st.session_state['detail_tconst'] = None
        st.rerun()