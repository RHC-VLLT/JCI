import ast
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Définition de la valeur par défaut du selectbox
DEFAULT_SELECT_OPTION = " Tapez le nom d'un film"

# ==================== 1. CONFIGURATION & STYLE (Incluant la Navbar Fixe) ====================
st.set_page_config(
    page_title="Recommandation de films", 
    page_icon="🎬", 
    layout="wide"
)

# ==================== 2. FONCTIONS UTILITAIRES ====================

### MODIFICATION : ÉTAPE 2 ###
# Suppression de handle_selection() et simple_substring_search_movies()

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

# Les fonctions de chargement et de recommandation restent inchangées

# ==================== 3. CHARGEMENT ET CONSTRUCTION DU MODÈLE ====================

@st.cache_data
def load_data():
    """Charge et prépare les données brutes."""
    try:
        # NOTE IMPORTANTE : Assurez-vous d'avoir un fichier 'intermediaire.csv' ou mettez-le à jour
        # Si vous n'avez pas intermediaire.csv, vous devez supprimer df_link = pd.read_csv("intermediaire.csv")
        df_movie = pd.read_csv("movie.csv")
        text_cols = ["keywords", "movie_overview_fr", "movie_overview",
                     "movie_tagline_fr", "movie_genres_y", "movie_original_title",
                     "movie_poster_url_fr", "title"] 
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
        
        df_people = pd.read_csv("intervenants.csv").rename(columns={
            "intervenant_primaryName": "person_name",
            "intervenant_primaryProfession": "person_professions",
            "intervenant_birthYear": "person_birthYear",
            "intervenant_deathYear": "person_deathYear",
        })
        # Si vous n'avez pas ce fichier, commentez la ligne ci-dessous
        df_link = pd.read_csv("intermediaire.csv")
        
        # Ajout d'une colonne de mapping pour faciliter la recherche inverse
        # C'est l'adaptation nécessaire pour passer du titre d'affichage au titre de travail (original)
        df_movie['title_to_original'] = df_movie.apply(
            lambda row: row['movie_original_title'] if row['title'] else row['movie_original_title'], axis=1
        )
        # Gestion des doublons pour le selectbox si 'title' n'est pas unique
        df_movie.drop_duplicates(subset=['title'], inplace=True) 

        return df_movie, df_people, df_link
    
    except FileNotFoundError as e:
        st.error(f" Fichier de données non trouvé : **{e.filename}**. Assurez-vous d'avoir les fichiers 'movie.csv', 'intervenants.csv', et 'intermediaire.csv' au bon endroit.")
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
    """Calcule et renvoie les recommandations. Note: movie_title est le titre original (movie_original_title)."""
    # Ici, nous utilisons l'original_title pour la recherche interne, 
    # mais pour le selectbox, nous utilisons le titre d'affichage ('title'). 
    # Assurez-vous que l'indexation se fait correctement.
    
    matches = df_movie[df_movie["movie_original_title"].str.lower() == movie_title.lower()]
    if matches.empty:
        # Cas où le titre est le 'title' d'affichage
        matches = df_movie[df_movie["title"].str.lower() == movie_title.lower()]

    if matches.empty:
        return None, f"Film non trouvé : '{movie_title}'. Veuillez vérifier la casse ou le titre original."
    
    movie_idx = matches.index[0]
    
    sim_keywords = cosine_similarity(recommender_data["keywords_matrix"][movie_idx], recommender_data["keywords_matrix"])[0]
    sim_overview = np.zeros(len(df_movie))
    sim_numeric = np.zeros(len(df_movie))
    sim_genres = cosine_similarity(recommender_data["genres_matrix"][movie_idx], recommender_data["genres_matrix"])[0]
    
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
        display_title = movie_data["title"] if movie_data["title"] else movie_data["movie_original_title"]
        recommendations.append({
            "title": display_title,
            "tconst": movie_data["tconst"],
            "similarity": hybrid_score[idx] * 100,
            "sim_keywords": sim_keywords[idx] * 100,
            "sim_overview": 0.0, 
            "sim_genres": sim_genres[idx] * 100,
            "sim_numeric": 0.0, 
            "genres": movie_data.get("movie_genres_y", "N/A"),
            "overview": movie_data.get("movie_overview_fr", movie_data.get("movie_overview", "")),
            "tagline": movie_data.get("movie_tagline_fr", movie_data.get("movie_tagline", "")),
            "poster": movie_data.get("movie_poster_url_fr", ""), 
        })
    
    return recommendations, None

# ==================== 4. INTERFACE PRINCIPALE (Streamlit) ====================

# Chargement
with st.spinner(" Chargement et préparation du modèle..."):
    df_movie, df_people, df_link = load_data()
    recommender_data = build_advanced_recommender(df_movie)

st.title("🎬 Système de Recommandation Intelligent")
st.markdown("Recommandations avancées basées sur **Contenu Pur** : **Style** (Keywords/Réalisateur) et **Genre**.")
st.markdown("---")


# --- DÉBUT DE LA BARRE DE NAVIGATION FIXE ---
with st.container():
    
    ### MODIFICATION : ÉTAPE 3 (Structure des colonnes) ###
    # Les colonnes sont ajustées pour faire de la place au simple selectbox
    col_kw, col_genre, col_reco, col_search_simple = st.columns([1.5, 1.5, 0.7, 5])

    # 1. PARAMÈTRES AVANCÉS (Inchangé)
    with col_kw:
        weight_keywords_raw = st.slider("Style", 0.0, 1.0, 0.50, 0.05, key="slider_kw", help="Importance du style/mots-clés.")

    with col_genre:
        weight_genres_raw = st.slider("Genre", 0.0, 1.0, 0.50, 0.05, key="slider_genre", help="Importance des catégories de films.")

    with col_reco:
        n_recos = st.selectbox("N Recos", [3, 5, 7, 10], index=1, key="select_nrecos", help="Nombre de films recommandés à afficher")
        
    # Calcul des poids (Inchangé)
    total_weight = weight_keywords_raw + weight_genres_raw
    if total_weight > 0:
        weight_keywords = weight_keywords_raw / total_weight
        weight_genres = weight_genres_raw / total_weight
        weight_overview = 0.0
        weight_numeric = 0.0
    else:
        weight_keywords, weight_overview, weight_genres, weight_numeric = 0.5, 0.0, 0.5, 0.0
    
    st.markdown("---") 

    ### MODIFICATION : ÉTAPE 4 (Implémentation du Selectbox simple) ###
    with col_search_simple:
        # Création de la liste d'options complète
        movie_titles_for_selectbox = [DEFAULT_SELECT_OPTION] + sorted(df_movie['title'].unique().tolist())
        
        selected_movie_title_display = st.selectbox(
            label="Barre de recherche",
            options=movie_titles_for_selectbox,
            index=0,
            placeholder=DEFAULT_SELECT_OPTION,
            label_visibility="collapsed",
            key="simple_movie_selector"
        )
        
    st.markdown('</div>', unsafe_allow_html=True) # Fin du fixed-navbar
