import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from utils import build_text_features, get_poster_url

@st.cache_data
def load_data():
    df_movie = pd.read_csv("../data/movie.csv")
    df_people = pd.read_csv("../data/intervenants.csv").rename(columns={
        "intervenant_primaryName": "person_name", 
        "intervenant_primaryProfession": "person_professions"
    })
    df_link = pd.read_csv("../data/intermediaire.csv")
    
    df_movie['display_title'] = df_movie.apply(lambda r: r['title'] if pd.notna(r['title']) else r['movie_original_title'], axis=1)
    df_movie = df_movie.drop_duplicates(subset=['display_title'])
    
    text_features = df_movie.apply(build_text_features, axis=1, result_type='expand')
    df_movie["keywords_text"], df_movie["overview_text"], df_movie["genres_text"] = text_features[0], text_features[1], text_features[2]
    return df_movie, df_people, df_link

def get_movie_cast_info(tconst, df_link, df_people):
    merged = df_link[df_link['tconst'] == tconst].merge(df_people, on="nconst")
    reals = merged[merged['person_professions'].str.contains('director', na=False)]['person_name'].unique().tolist()
    actors = merged[merged['person_professions'].str.contains('actor|actress', na=False)].head(5)
    cast_list = []
    for _, row in actors.iterrows():
        cast_list.append({"name": row['person_name'], "photo": row.get('tmdb_profile_url')})
    return reals, cast_list

@st.cache_resource
def build_recommender(df_movie):
    tfidf_k = TfidfVectorizer(max_features=500, stop_words='english')
    k_mat = tfidf_k.fit_transform(df_movie["keywords_text"])
    tfidf_g = TfidfVectorizer(max_features=50)
    g_mat = tfidf_g.fit_transform(df_movie["genres_text"])
    return {"keywords_matrix": k_mat, "genres_matrix": g_mat}

def recommend_movies(movie_title, df_movie, recommender_data):
    matches = df_movie[df_movie["display_title"].str.lower() == movie_title.lower()]
    if matches.empty: return None
    idx = matches.index[0]
    sim_k = cosine_similarity(recommender_data["keywords_matrix"][idx], recommender_data["keywords_matrix"])[0]
    sim_g = cosine_similarity(recommender_data["genres_matrix"][idx], recommender_data["genres_matrix"])[0]
    score = (0.35 * sim_k + 1.0 * sim_g) / 1.35
    indices = np.argsort(score)[::-1][1:11]
    return [{**df_movie.iloc[i].to_dict(), "score_sim": score[i]*100, "poster_url": get_poster_url(df_movie.iloc[i])} for i in indices]