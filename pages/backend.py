import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import build_text_features, get_poster_url

WEIGHT_KEYWORDS = 0.35
WEIGHT_GENRES = 1.00

@st.cache_data
def load_data():
    try:
        df_movie = pd.read_csv("../data/movie.csv")
        text_cols = ["keywords", "movie_overview_fr", "movie_overview", "movie_tagline_fr", "movie_genres_y", "title", "movie_original_title"]
        for col in text_cols:
            if col in df_movie.columns: df_movie[col] = df_movie[col].fillna("")
        
        text_features = df_movie.apply(build_text_features, axis=1, result_type='expand')
        df_movie["keywords_text"], df_movie["overview_text"], df_movie["genres_text"] = text_features[0], text_features[1], text_features[2]
        
        df_people = pd.read_csv("../data/intervenants.csv").rename(columns={"intervenant_primaryName": "person_name", "intervenant_primaryProfession": "person_professions"})
        df_link = pd.read_csv("../data/intermediaire.csv")
        
        df_movie['display_title'] = df_movie.apply(lambda row: row['title'] if row['title'] else row['movie_original_title'], axis=1)
        df_movie = df_movie[df_movie['display_title'] != ""].drop_duplicates(subset=['display_title'])
        return df_movie, df_people, df_link
    except Exception as e:
        st.error(f"Erreur chargement: {e}"); st.stop()

@st.cache_resource
def build_recommender(df_movie):
    tfidf_k = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
    k_mat = tfidf_k.fit_transform(df_movie["keywords_text"])
    tfidf_g = TfidfVectorizer(max_features=50)
    g_mat = tfidf_g.fit_transform(df_movie["genres_text"])
    return {"keywords_matrix": k_mat, "genres_matrix": g_mat}

def recommend_movies(movie_title, df_movie, recommender_data, n_recommendations=30):
    matches = df_movie[df_movie["display_title"].str.lower() == movie_title.lower()]
    if matches.empty: return None, "Film non trouvé"
    movie_idx = matches.index[0]
    sim_k = cosine_similarity(recommender_data["keywords_matrix"][movie_idx], recommender_data["keywords_matrix"])[0]
    sim_g = cosine_similarity(recommender_data["genres_matrix"][movie_idx], recommender_data["genres_matrix"])[0]
    score = (WEIGHT_KEYWORDS * sim_k + WEIGHT_GENRES * sim_g) / (WEIGHT_KEYWORDS + WEIGHT_GENRES)
    indices = np.argsort(score)[::-1]
    final_indices = [idx for idx in indices if idx != movie_idx][:n_recommendations]
    
    recos = []
    for idx in final_indices:
        movie_data = df_movie.iloc[idx]
        recos.append({
            "titre": movie_data["display_title"], "tconst": movie_data["tconst"], "score_sim": score[idx] * 100,
            "annee": int(movie_data.get("movie_startYear", 0)), "genres": movie_data.get("movie_genres_y", "N/A"),
            "poster_url": get_poster_url(movie_data), "overview": movie_data.get("movie_overview_fr", movie_data.get("movie_overview", ""))
        })
    return recos, None