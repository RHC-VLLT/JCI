import streamlit as st
import pickle
import pandas as pd
import numpy as np

# ------------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE
# ------------------------------------------------------------------------------
st.set_page_config(page_title="Recommandeur de Films", page_icon="🎬")

# ------------------------------------------------------------------------------
# 2. CHARGEMENT DES DONNÉES (CACHE)
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    # ATTENTION : On charge les fichiers depuis le sous-dossier 'notebook/'
    # car votre app.py est à la racine, mais les pkl sont dans le dossier notebook.
    try:
        df = pickle.load(open('notebook/movies.pkl', 'rb'))
        X = pickle.load(open('notebook/X_matrix.pkl', 'rb'))
        model_knn = pickle.load(open('notebook/knn_model.pkl', 'rb'))
        return df, X, model_knn
    except FileNotFoundError:
        st.error("Erreur : Fichiers introuvables. Vérifiez que 'movies.pkl', 'X_matrix.pkl' et 'knn_model.pkl' sont bien dans le dossier 'notebook'.")
        return None, None, None

df, X, model_knn = load_data()

# ------------------------------------------------------------------------------
# 3. FONCTION DE RECOMMANDATION (LOGIQUE KNN)
# ------------------------------------------------------------------------------
def recommend(movie_title):
    # Si les données n'ont pas chargé, on arrête
    if df is None:
        return []

    # 1. Trouver l'index du film dans le DataFrame
    try:
        # Recherche insensible à la casse (lower case)
        movie_index = df[df['title'].str.lower() == movie_title.lower()].index[0]
    except IndexError:
        return ["Film introuvable"]

    # 2. Récupérer les vecteurs (features) de ce film dans la matrice X
    # On reshape pour que Scikit-Learn comprenne que c'est une seule ligne
    movie_features = X.iloc[movie_index].values.reshape(1, -1)

    # 3. Lancer la recherche des voisins (KNN)
    # On demande 6 voisins car le premier est toujours le film lui-même
    distances, indices = model_knn.kneighbors(movie_features, n_neighbors=6)

    # 4. Récupérer les titres
    recommendations = []
    # On commence la boucle à 1 (et pas 0) pour exclure le film lui-même
    for i in range(1, len(indices.flatten())):
        idx = indices.flatten()[i]
        recommendations.append(df.iloc[idx]['title'])

    return recommendations
#------------------------------------------------------------------------------
# 4. INTERFACE UTILISATEUR (UI) MODIFIÉE
# ------------------------------------------------------------------------------
st.title('🎬 Mon Recommandeur de Films')
st.markdown("Bienvenue ! Cherchez un film pour découvrir des pépites similaires.")

# Vérification de sécurité
if df is not None:
    
    # --- MODIFICATION ICI : SEARCHBAR ---
    # On utilise index=None pour ne rien sélectionner au début
    # On utilise placeholder pour inviter à la recherche
    selected_movie = st.selectbox(
        label="Barre de recherche",
        options=df['title'].values,
        index=None,                  # Aucun film sélectionné par défaut
        placeholder="🔍 Tapez le nom d'un film (ex: Batman)...", # Texte grisé
        label_visibility="collapsed" # Cache le label "Barre de recherche" pour faire plus épuré
    )

    # On lance la recommandation seulement si un film est choisi
    if selected_movie:
        st.write(f"Recherche pour : **{selected_movie}**") # Petit feedback visuel
        
        with st.spinner('Calcul en cours...'):
            recos = recommend(selected_movie)
        
        st.divider() # Ligne de séparation esthétique
        st.subheader("Nos recommandations :")
        
        # Affichage
        for i, movie in enumerate(recos):
            st.success(f"**{i+1}.** {movie}")

else:
    st.warning("Les données ne sont pas chargées.")