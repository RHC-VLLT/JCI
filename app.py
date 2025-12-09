import streamlit as st
import pickle
import pandas as pd
import numpy as np

# ------------------------------------------------------------------------------
# 1. CONFIGURATION DE LA PAGE & STYLISME
# ------------------------------------------------------------------------------
st.set_page_config(layout="wide", page_title="Just Creuse It - Recommandations", page_icon="🎬")

# Le Design (CSS personnalisé)
st.markdown("""
<style>
       /* Fond de la page en NOIR */
        .stApp {
        background-color: black;
    }
       /* Tout le texte en BLANC (Sauf là où les couleurs sont forcées) */
        h1, h2, h3, p, div, label {
        color: white;
    }
       /* Style spécifique pour le conteneur des succès pour qu'il soit sur fond noir */
        .stSuccess {
            background-color: #333333 !important; /* Fond gris foncé pour le succès */
            color: white !important; /* Texte blanc sur le fond gris */
            border-radius: 5px;
            border: 1px solid #D7001D; /* Bordure rouge pour un look "Cinéma" */
    }
    .stSuccess > div {
        color: white !important; /* Assure que le texte du succès reste blanc */
    }

       /* La Barre de Navigation (Centrée) */
        .navbar {
            padding: 20px;
           text-align: center;
            background-color: black;
            border-bottom: 1px solid #333;
            margin-bottom: 30px;
    }
        .navbar a {
            color: white;
            text-decoration: none;
           margin: 0 20px;
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
    }
        .navbar a:hover {
           color: #D7001D; /* Rouge au survol */
    }
    
       /* NOUVEAU: Style pour le conteneur principal ROUGE */
        .main-content-box {
            width: 100%; /* Sera limité à 70% par la colonne englobante */
            margin: 0 auto;
            background-color: #D7001D; /* Couleur rouge */
            border: 2px solid black; /* Bordure noire */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.5); 
        }
        .main-content-box h2, .main-content-box h3, .main-content-box p, .main-content-box label {
            color: white; 
        }
        
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 2. CHARGEMENT DES DONNÉES (LOGIQUE ML)
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # Assurez-vous que le chemin 'notebook/' est correct
        df = pickle.load(open('notebook/movies.pkl', 'rb'))
        X = pickle.load(open('notebook/X_matrix.pkl', 'rb'))
        model_knn = pickle.load(open('notebook/knn_model.pkl', 'rb'))
        return df, X, model_knn
    except FileNotFoundError:
        st.error("Erreur : Fichiers introuvables. Vérifiez le dossier 'notebook/'.")
        return None, None, None

df, X, model_knn = load_data()


# ------------------------------------------------------------------------------
# 3. FONCTION DE RECOMMANDATION (LOGIQUE ML)
# ------------------------------------------------------------------------------
def recommend(movie_title):
    if df is None:
        return []

    try:
        # 1. Trouver l'index du film
        movie_index = df[df['title'].str.lower() == movie_title.lower()].index[0]
        
        # 2. Récupérer les vecteurs (features)
        movie_features = X.iloc[movie_index].values.reshape(1, -1)
        
        # 3. Lancer la recherche des voisins (KNN)
        distances, indices = model_knn.kneighbors(movie_features, n_neighbors=6)
        
        # 4. Récupérer les titres (exclure le film lui-même)
        recommendations = [df.iloc[idx]['title'] for idx in indices.flatten()[1:]]
        
        return recommendations
    except IndexError:
        return ["Film introuvable. Veuillez vérifier le titre."]


# ------------------------------------------------------------------------------
# 4. INTERFACE UTILISATEUR & MOTEUR DE RECOMMANDATION (DIV ROUGE)
# ------------------------------------------------------------------------------

# --- BARRE DE NAVIGATION ---
st.markdown("""
    <div class="navbar">
        <a href="#"> Accueil</a>
        <a href="#"> Films</a>
        <a href="#"> Séries</a>
        <a href="#"> Recherche</a>
    </div>
""", unsafe_allow_html=True)

# --- Conteneur 70% de largeur (Boîte Rouge) ---
c_L, c_M, c_R = st.columns([15, 70, 15]) 

with c_M:
    # OUVRE LA DIV ROUGE
    st.markdown('<div class="main-content-box">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: white;'>MOTEUR DE RECOMMANDATION</h2>", unsafe_allow_html=True)

    if df is not None:
        # Barre de sélection/recherche
        selected_movie = st.selectbox(
            label="Barre de recherche",
            options=df['title'].values,
            index=None,
            placeholder="🔍 Tapez le nom d'un film (ex: Batman, Avatar)...",
            label_visibility="collapsed"
        )

        # On lance la recommandation seulement si un film est choisi
        if selected_movie:
            
            with st.spinner(f'Calcul des films similaires à "{selected_movie}"...'):
                recos = recommend(selected_movie)

            st.markdown("<hr style='border: 1px solid black; margin: 20px 0;'>", unsafe_allow_html=True)
            
            # Affichage du titre principal
            st.subheader(f"Les 5 pépites similaires à **{selected_movie}** :")
            
            # Utilisation d'une structure en 5 colonnes pour afficher 5 recommandations (Image + Titre)
            cols = st.columns(5)
            
            for i, movie in enumerate(recos):
                
                if i < 5:
                    
                    with cols[i]:
                        
                        if movie == "Film introuvable. Veuillez vérifier le titre.":
                            st.warning(movie)
                            continue
                            
                        # Récupérer l'URL du poster
                        try:
                            # *****************************************************************
                            # MODIFICATION ICI : On utilise 'movie_poster_path_1'
                            # *****************************************************************
                            poster_url = df[df['title'] == movie]['movie_poster_path_1'].iloc[0]
                            
                            # Affiche l'image avec un titre en dessous
                            st.image(poster_url, caption=f"{i+1}. {movie}", use_container_width=True)
                            
                        except IndexError:
                            st.info(f"Image ou titre manquant dans le DataFrame pour : {movie}")
                            st.markdown(f"**{i+1}.** {movie}")
                        except KeyError:
                            # Cette erreur ne devrait plus se produire si 'movie_poster_path_1' existe.
                            st.error("Erreur: La colonne 'movie_poster_path_1' est introuvable. (Vérifiez le .pkl)")
                            st.markdown(f"**{i+1}.** {movie}")


    else:
        st.warning("⚠️ Impossible de lancer la recommandation : Le chargement des données a échoué. (Vérifiez le dossier 'notebook/')")
        
    # FERME LA DIV ROUGE
    st.markdown('</div>', unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 5. CONTENU DE LA PAGE D'ACCUEIL (POPCORN/VIDEO)
# ------------------------------------------------------------------------------

st.markdown("<hr style='border: 1px solid #333; margin: 50px 0;'>", unsafe_allow_html=True)

# L'image et la Vidéo pour la page d'accueil (Si vous les gardez)
col1, col2 = st.columns([1, 1], gap="medium")
with col1:
    try:
        st.image("popcorn.jpg", use_container_width=True)
    except:
        st.info("ℹ️ Placeholder Image 'popcorn.jpg' introuvable.")

with col2:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.title("LE CINÉMA QUI FAIT BATTRE LE CŒUR CREUSOIS")
    st.write("Découvrez les meilleures pépites locales.")
    st.button("VOIR LE FILM SUGGÉRÉ")

st.markdown("<hr style='border: 1px solid #333; margin: 50px 0;'>", unsafe_allow_html=True)

st.markdown("<h2 style='text-align: center;'>VOTRE VIDÉO</h2>", unsafe_allow_html=True)
c_left, c_center, c_right = st.columns([1, 3, 1])
with c_center:
    try:
        st.video("scooby.mp4")
    except:
        st.info("ℹ️ Placeholder Vidéo 'scooby.mp4' introuvable.")