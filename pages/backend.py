import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import build_text_features, get_poster_url

# Poids pour l'algo
WEIGHT_KEYWORDS = 0.35
WEIGHT_GENRES = 1.00

@st.cache_data
def load_data():
    """Charge et nettoie les données CSV."""
    try:
        # Notez le ../ car nous sommes dans le dossier pages/
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
        
        # Création des features textuelles
        text_features = df_movie.apply(build_text_features, axis=1, result_type='expand')
        df_movie["keywords_text"] = text_features[0]
        df_movie["overview_text"] = text_features[1]
        df_movie["genres_text"] = text_features[2]
        
        df_people = pd.read_csv("../data/intervenants.csv").rename(columns={
            "intervenant_primaryName": "person_name",
            "intervenant_primaryProfession": "person_professions"
        })
        df_link = pd.read_csv("../data/intermediaire.csv")
        
        # Nettoyage titres doublons
        df_movie['display_title'] = df_movie.apply(
            lambda row: row['title'] if row['title'] else row['movie_original_title'], axis=1
        )
        df_movie = df_movie[df_movie['display_title'] != ""].drop_duplicates(subset=['display_title'])
        
        return df_movie, df_people, df_link
    except FileNotFoundError as e:
        st.error(f"Fichier non trouvé (Vérifiez le dossier data): {e}")
        st.stop()
    except Exception as e:
        st.error(f"Erreur chargement données: {e}")
        st.stop()

@st.cache_resource
def build_recommender(df_movie):
    """Construit les matrices TF-IDF."""
    try:
        tfidf_keywords = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
        keywords_matrix = tfidf_keywords.fit_transform(df_movie["keywords_text"])
        
        tfidf_genres = TfidfVectorizer(max_features=50)
        genres_matrix = tfidf_genres.fit_transform(df_movie["genres_text"])
        
        return {"keywords_matrix": keywords_matrix, "genres_matrix": genres_matrix}
    except Exception as e:
        st.error(f"Erreur modèle: {e}")
        st.stop()

def recommend_movies(movie_title, df_movie, recommender_data, n_recommendations=30):
    """Calcule les recommandations."""
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
            "genres": movie_data.get("movie_genres_y", "N/A"),
            "poster_url": get_poster_url(movie_data),
            "overview": movie_data.get("movie_overview_fr", movie_data.get("movie_overview", "")),
        })
    
    return recommendations, None