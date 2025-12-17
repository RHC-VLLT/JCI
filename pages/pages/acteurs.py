import streamlit as st
import pandas as pd
import sys
import os

# Ajustement des chemins pour importer les modules du dossier parent
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import config
import backend

# ================== CONFIGURATION ==================
st.set_page_config(page_title="CinéStream - Acteurs", layout="wide", page_icon="🎭", initial_sidebar_state="collapsed")

# ================== CSS (VOTRE STYLE DARK / APPLE TV) ==================
# On injecte d'abord le CSS global pour le background, puis votre CSS spécifique par dessus
config.inject_css()

st.markdown(
    """
    <style>
    /* Carte Bio (à droite) */
    .actor-card {
        border: 1px solid #333;
        border-radius: 12px;
        padding: 24px;
        background: linear-gradient(180deg, rgba(30,30,30,0.95) 0%, rgba(10,10,10,0.95) 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        margin-top: 20px;
    }

    /* Nom de l'acteur */
    .actor-name-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-align: center;
        color: #D7001D; /* Rouge JCI */
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }

    /* Images */
    img {
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
    }
    
    /* Input Recherche */
    div[data-baseweb="select"] {
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ================== CHARGEMENT DES DONNÉES ==================
# On utilise le backend existant pour ne pas charger les CSV deux fois
df_movies, df_actors, df_links = backend.load_data()

# ================== FONCTIONS UTILES ==================

def get_profile_url(row):
    """Récupère l'image de l'acteur."""
    # Adaptation selon les colonnes de votre backend
    if 'tmdb_profile_url' in row.index and pd.notna(row['tmdb_profile_url']):
        return row['tmdb_profile_url']
    return "https://via.placeholder.com/300x450?text=No+Image"

def translate_profession(prof):
    """Traduit les métiers en français proprement"""
    if not isinstance(prof, str): return ""
    trad = {
        "actor": "Acteur", "actress": "Actrice", "director": "Réalisateur",
        "writer": "Scénariste", "producer": "Producteur", "composer": "Compositeur"
    }
    parts = [p.strip().lower() for p in prof.split(",")]
    return ", ".join([trad.get(p, p.capitalize()) for p in parts])

# ================== INTERFACE UTILISATEUR ==================

# Navbar simplifiée pour le retour
c_logo, c_nav = st.columns([1, 4])
with c_logo:
    # On réutilise votre logo via config
    logo_b64 = config.load_base64_image(config.LOGO_PATH)
    if logo_b64:
        st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="100">', unsafe_allow_html=True)
        
with c_nav:
    if st.button("🏠 RETOUR ACCUEIL", key="home_btn"):
        st.switch_page("appp.py")

st.markdown("<h1 style='text-align:center;'>EXPLORATEUR DE TALENTS 🎭</h1>", unsafe_allow_html=True)

# --- ÉTAT DE SESSION ---
if 'selected_actor_id' not in st.session_state:
    st.session_state.selected_actor_id = None

# --- BARRE DE RECHERCHE ---
# Note: On utilise 'person_name' car c'est le nom de colonne standardisé dans votre backend.py
if not df_actors.empty:
    all_names = sorted(df_actors['person_name'].dropna().unique().tolist())
else:
    all_names = []

col_search, col_btn = st.columns([4, 1])

with col_search:
    search_name = st.selectbox(
        "Rechercher un talent",
        options=[""] + all_names,
        format_func=lambda x: "🔎 Chercher un acteur, réalisateur..." if x == "" else x,
        label_visibility="collapsed"
    )

with col_btn:
    if st.button("RECHERCHER", use_container_width=True):
        if search_name:
            found = df_actors[df_actors['person_name'] == search_name]
            if not found.empty:
                st.session_state.selected_actor_id = found.iloc[0]['nconst']
                st.rerun()

st.markdown("---")

# ================== AFFICHAGE DYNAMIQUE ==================

if st.session_state.selected_actor_id:
    # >>> CAS 1 : UN ACTEUR EST SÉLECTIONNÉ
    
    # Récupérer les données
    actor = df_actors[df_actors['nconst'] == st.session_state.selected_actor_id].iloc[0]
    
    if st.button("⬅ Retour aux tendances"):
        st.session_state.selected_actor_id = None
        st.rerun()

    # Mise en page : Photo à gauche, Bio à droite
    col_img, col_info = st.columns([1, 2.5], gap="large")
    
    with col_img:
        st.image(get_profile_url(actor), use_container_width=True)
        st.markdown(f"<div class='actor-name-title'>{actor['person_name']}</div>", unsafe_allow_html=True)

    with col_info:
        # Carte d'info
        st.markdown('<div class="actor-card">', unsafe_allow_html=True)
        
        prof_str = translate_profession(actor.get('person_professions', ''))
        birth_year = int(actor['person_birthYear']) if pd.notna(actor.get('person_birthYear')) else "?"
        
        st.markdown(f"**Métier :** {prof_str}")
        st.markdown(f"**Année de naissance :** {birth_year}")
        
        st.markdown("### Biographie")
        bio = actor.get('tmdb_biography_fr', "Biographie non disponible.")
        st.write(bio if pd.notna(bio) else "Biographie non disponible.")
            
        st.markdown("</div>", unsafe_allow_html=True)

    # Section Filmographie
    st.markdown("### 🎞️ Filmographie associée")
    
    # Jointure via df_links
    actor_tconsts = df_links[df_links['nconst'] == actor['nconst']]['tconst'].tolist()
    
    if actor_tconsts:
        my_movies = df_movies[df_movies['tconst'].isin(actor_tconsts)]
        
        if not my_movies.empty:
            # Tri par année
            if 'movie_startYear' in my_movies.columns:
                my_movies = my_movies.sort_values('movie_startYear', ascending=False)
                
            cols = st.columns(5)
            for i, (_, film) in enumerate(my_movies.iterrows()):
                with cols[i % 5]:
                    # Affiche du film (Logique du backend)
                    poster = film.get('movie_poster_url_fr')
                    if pd.isna(poster): poster = film.get('movie_poster_path_1')
                    if pd.isna(poster) and 'movie_poster_path_fr' in film:
                         poster = f"https://image.tmdb.org/t/p/w500{film['movie_poster_path_fr']}"
                    
                    if pd.notna(poster) and str(poster).startswith("http"):
                        st.image(poster, use_container_width=True)
                    else:
                        st.info("No Image")
                    
                    st.caption(f"**{film.get('display_title', 'Sans titre')}**")
        else:
            st.info("Aucun détail de film trouvé.")
    else:
        st.info("Cet acteur n'est lié à aucun film dans la base.")

else:
    # >>> CAS 2 : ACCUEIL (GRILLE TENDANCE)
    st.subheader("🔥 En vedette")
    
    # On prend les 12 premiers acteurs
    top_actors = df_actors.head(12)
        
    cols = st.columns(6)
    for idx, (_, row) in enumerate(top_actors.iterrows()):
        with cols[idx % 6]:
            img_path = get_profile_url(row)
            st.image(img_path, use_container_width=True)
            
            st.markdown(f"**{row['person_name']}**")
            
            if st.button("Voir profil", key=f"home_{row['nconst']}"):
                st.session_state.selected_actor_id = row['nconst']
                st.rerun()