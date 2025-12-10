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
       /* Fond de la page en NOIR par défaut */
        .stApp {
            background-color: black;
        }
       /* Tout le texte en BLANC (Sauf là où les couleurs sont forcées) */
        h1, h2, h3, p, div, label {
            color: white;
        }
       /* Style spécifique pour les succès sur fond noir */
        .stSuccess {
            background-color: #333333 !important;
            color: white !important;
            border-radius: 5px;
            border: 1px solid #D7001D;
        }
    
       /* NOUVEAU: Conteneur de la section d'accueil. On utilise deux conteneurs internes pour les couleurs. */
        .accueil-container {
            width: 100%;
            margin: 0;
            padding: 0;
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
            color: #D7001D;
    }
    
       /* Conteneur du Moteur de Recommandation */
        .main-content-box {
            width: 100%;
            margin: 0 auto;
            background-color: #111111; /* Fond gris très foncé dans le noir pour démarcation */
            border: 2px solid #D7001D; /* Bordure ROUGE */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 0 15px rgba(215, 0, 29, 0.5); /* Ombre rouge */
        }
        .main-content-box h2, .main-content-box h3, .main-content-box p, .main-content-box label {
            color: white; 
        }
        
        /* Ajustements pour les colonnes Streamlit (IMPORTANT pour le design du header) */
        /* Supprime le padding par défaut des colonnes */
        .stColumns > div {
            padding: 0px !important;
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
        movie_index = df[df['title'].str.lower() == movie_title.lower()].index[0]
        movie_features = X.iloc[movie_index].values.reshape(1, -1)
        distances, indices = model_knn.kneighbors(movie_features, n_neighbors=6)
        recommendations = [df.iloc[idx]['title'] for idx in indices.flatten()[1:]]
        return recommendations
    except IndexError:
        return ["Film introuvable. Veuillez vérifier le titre."]


# ------------------------------------------------------------------------------
# 4. CONTENU DE LA PAGE D'ACCUEIL (RÉPLICATION EXACTE DE LA CAPTURE)
# ------------------------------------------------------------------------------

# --- BARRE DE NAVIGATION (Reste en haut, en noir) ---
st.markdown("""
    <div class="navbar">
        <a href="#"> Accueil</a>
        <a href="#"> Films</a>
        <a href="#"> Séries</a>
        <a href="#"> Recherche</a>
    </div>
""", unsafe_allow_html=True)

# --- Conteneur 90% de largeur (Centrage de la section d'accueil) ---
c_L_bande, c_M_bande, c_R_bande = st.columns([5, 90, 5])

with c_M_bande:
    # --- CONTENU INTERNE (Image à gauche, Texte à droite) ---
    # Utilisez une seule colonne pour l'encapsulation si besoin, sinon utilisez directement col1, col2
    
    col1, col2 = st.columns([1, 1], gap="small") # gap="small" pour les rapprocher
    
    # ***** COLONNE IMAGE (FOND ROUGE) *****
    with col1:
        # Utilisation d'une div interne pour forcer le fond rouge autour de l'image
        try:
            # L'image prend 100% de la colonne [1]
            st.image("assets/pop_corn.jpg", use_container_width=True) 
        except:
            st.warning("⚠️ Image d'accueil 'assets/pop_corn.jpg' introuvable.")
            st.markdown(f'<div style="height: auto; widht: 90%"></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


    # ***** COLONNE TEXTE (FOND NOIR) *****
    with col2:
        # Utilisation d'une div interne pour forcer le fond noir autour du texte
        st.markdown(f'<div style="background-color: black; padding: 20px; height: 100%; display: flex; flex-direction: column; justify-content: center;">', unsafe_allow_html=True)
        
        # Le titre est blanc par défaut sur le fond noir de la div interne
        st.title("LE CINÉMA QUI FAIT BATTRE LE CŒUR CREUSOIS")
        st.write("Découvrez les meilleures pépites locales.")
        
        # Bouton stylisé en ROUGE
        st.markdown("""
            <style>
                div[data-testid="stColumn"] button {
                    background-color: #D7001D !important; 
                    color: white !important; 
                    border: none !important;
                    padding: 10px 20px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            </style>
        """, unsafe_allow_html=True)
        st.button("LE FILM PARFAIT à la Carte >>>")

        st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 5. MOTEUR DE RECOMMANDATION (DIV ROUGE/NOIRE CENTRÉE)
# ------------------------------------------------------------------------------

# Ligne de séparation pour descendre du rouge (la ligne est maintenant en noir sur noir, invisible, mais elle crée de l'espace)
st.markdown("<hr style='border: 1px solid #333; margin: 30px 0;'>", unsafe_allow_html=True)

# Centrage du moteur à 70% de la largeur
c_L, c_M, c_R = st.columns([15, 70, 15]) 

with c_M:
    # OUVRE LA DIV du MOTEUR
    st.markdown('<div class="main-content-box">', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align: center; color: #D7001D;'>MOTEUR DE RECOMMANDATION</h2>", unsafe_allow_html=True)

    if df is not None:
        
        selected_movie = st.selectbox(
            label="Barre de recherche",
            options=df['title'].values,
            index=None,
            placeholder="🔍 Tapez le nom d'un film (ex: Batman, Avatar)...",
            label_visibility="collapsed"
        )

        if selected_movie:
            
            with st.spinner(f'Calcul des films similaires à "{selected_movie}"...'):
                recos = recommend(selected_movie)

            st.markdown("<hr style='border: 1px solid #D7001D; margin: 20px 0;'>", unsafe_allow_html=True)
            
            st.subheader(f"Les 5 pépites similaires à **{selected_movie}** :")
            
            cols = st.columns(5)
            
            for i, movie in enumerate(recos):
                
                if i < 5:
                    with cols[i]:
                        if movie == "Film introuvable. Veuillez vérifier le titre.":
                            st.warning(movie)
                            continue
                            
                        try:
                            # Utilisation de 'movie_poster_path_1'
                            poster_url = df[df['title'] == movie]['movie_poster_path_1'].iloc[0]
                            st.image(poster_url, caption=f"{i+1}. {movie}", use_container_width=True)
                            
                        except IndexError:
                            st.info(f"Titre manquant ou Image non trouvée pour : {movie}")
                            st.markdown(f"**{i+1}.** {movie}")
                        except KeyError:
                            st.error("Erreur: La colonne 'movie_poster_path_1' est introuvable.")
                            st.markdown(f"**{i+1}.** {movie}")


    else:
        st.warning("⚠️ Impossible de lancer la recommandation : Le chargement des données a échoué.")
        
    # FERME LA DIV du MOTEUR
    st.markdown('</div>', unsafe_allow_html=True)


# ------------------------------------------------------------------------------
# 7. VIDÉO SCOOBY (SECTION FINALE à 90% de largeur)
# ------------------------------------------------------------------------------
st.markdown("<hr style='border: 1px solid #333; margin: 50px 0;'>", unsafe_allow_html=True)

# Centrage de la section à 90% (5% vide + 90% contenu + 5% vide)
c_left, c_center, c_right = st.columns([5, 90, 5])

with c_center:
    # Le titre est centré dans la colonne de 90%
    st.markdown("<h2 style='text-align: center;'>VOTRE VIDÉO</h2>", unsafe_allow_html=True)
    
    try:
        st.image("assets/scoobydoo.png", use_container_width=True)
    except:
        st.info("ℹ️ Placeholder Image ou Vidéo introuvable.")