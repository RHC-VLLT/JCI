import streamlit as st
import pandas as pd
import config
import backend
from utils import get_poster_url

def show_acteurs():
    # --- CSS SPECIFIQUE ---
    st.markdown("""
    <style>
    .actor-card {
        border: 1px solid #333;
        border-radius: 12px;
        padding: 24px;
        background: linear-gradient(180deg, rgba(30,30,30,0.95) 0%, rgba(10,10,10,0.95) 100%);
        box-shadow: 0 10px 30px rgba(0,0,0,0.8);
        margin-top: 20px;
    }
    .actor-name-title {
        font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem;
        text-align: center; color: #D7001D;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    
    /* Uniformisation des images de la grille */
    div[data-testid="stImage"] img {
        height: 300px;
        object-fit: cover;
        border-radius: 8px;
    }

    /* Masquer le bouton standard s'il gêne */
    div[data-testid="stToolbar"] {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

    # --- CHARGEMENT DONNÉES ---
    df_movies, df_actors, df_links = backend.load_data()

    # --- FONCTIONS LOCALES ---
    def get_profile_url(row):
        """Retourne l'image de profil ou une image par défaut si absente."""
        # URL d'une image "Avatar par défaut" (libre de droit)
        default_img = "https://cdn.pixabay.com/photo/2015/10/05/22/37/blank-profile-picture-973460_1280.png"
        
        # Vérifie si la colonne existe
        if 'tmdb_profile_url' not in row.index:
            return default_img
            
        url = row['tmdb_profile_url']
        
        # Vérifie si l'URL est valide (pas vide, pas NaN)
        if pd.isna(url) or str(url).strip() == "" or str(url).lower() == "nan":
            return default_img
            
        return url

    def translate_profession(prof):
        if not isinstance(prof, str): return ""
        trad = {"actor": "Acteur", "actress": "Actrice", "director": "Réalisateur", "writer": "Scénariste"}
        parts = [p.strip().lower() for p in prof.split(",")]
        return ", ".join([trad.get(p, p.capitalize()) for p in parts])

    # --- HEADER / RETOUR ---
    c_logo, c_nav = st.columns([1, 4])
    with c_logo:
        logo_b64 = config.load_base64_image(config.LOGO_PATH)
        if logo_b64:
            st.markdown(f'<img src="data:image/png;base64,{logo_b64}" width="100">', unsafe_allow_html=True)
            
    with c_nav:
        # BOUTON RETOUR : On change juste la variable de session
        if st.button("🏠 RETOUR ACCUEIL", key="btn_back_home"):
            st.session_state['current_page'] = 'home'
            st.rerun()

    st.markdown("<h1 style='text-align:center;'>EXPLORATEUR DE TALENTS 🎭</h1>", unsafe_allow_html=True)
    st.markdown("---")

    # --- ÉTAT LOCAL ---
    if 'selected_actor_id' not in st.session_state:
        st.session_state.selected_actor_id = None

    # --- RECHERCHE ---
    if not df_actors.empty:
        # On s'assure que la colonne nom existe
        name_col = 'person_name' if 'person_name' in df_actors.columns else 'intervenant_primaryName'
        all_names = sorted(df_actors[name_col].dropna().unique().tolist())
    else:
        all_names = []

    c1, c2 = st.columns([4, 1])
    with c1:
        search_name = st.selectbox("Rechercher", [""] + all_names, label_visibility="collapsed")
    with c2:
        if st.button("CHERCHER", use_container_width=True):
            if search_name:
                found = df_actors[df_actors[name_col] == search_name]
                if not found.empty:
                    st.session_state.selected_actor_id = found.iloc[0]['nconst']
                    st.rerun()

    # --- AFFICHAGE ---
    if st.session_state.selected_actor_id:
        # MODE DETAIL
        actor = df_actors[df_actors['nconst'] == st.session_state.selected_actor_id].iloc[0]
        
        if st.button("⬅ Retour aux tendances"):
            st.session_state.selected_actor_id = None
            st.rerun()

        col1, col2 = st.columns([1, 2.5], gap="large")
        with col1:
            st.image(get_profile_url(actor), use_container_width=True)
            # Nom en dessous de l'image
            st.markdown(f"<div class='actor-name-title'>{actor[name_col]}</div>", unsafe_allow_html=True)
            
        with col2:
            st.markdown('<div class="actor-card">', unsafe_allow_html=True)
            prof = translate_profession(actor.get('person_professions', ''))
            st.markdown(f"**Métier:** {prof}")
            
            # Gestion année de naissance
            birth = actor.get('person_birthYear') or actor.get('intervenant_birthYear')
            year_display = int(birth) if pd.notna(birth) else "?"
            st.markdown(f"**Naissance:** {year_display}")
            
            st.markdown("### Biographie")
            st.write(actor.get('tmdb_biography_fr', 'Non disponible.'))
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Filmographie
        st.markdown("### 🎞️ Filmographie")
        tconsts = df_links[df_links['nconst'] == actor['nconst']]['tconst'].tolist()
        if tconsts:
            movies = df_movies[df_movies['tconst'].isin(tconsts)]
            if not movies.empty:
                # Tri par date
                if 'movie_startYear' in movies.columns:
                    movies = movies.sort_values('movie_startYear', ascending=False)
                    
                cols = st.columns(5)
                for i, (_, m) in enumerate(movies.iterrows()):
                    with cols[i % 5]:
                        poster = get_poster_url(m) # Importé de utils
                        if poster: 
                            st.image(poster, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/300x450?text=No+Poster", use_container_width=True)
                        st.caption(f"**{m.get('display_title')}**")
    else:
        # MODE GRILLE - EN VEDETTE
        st.subheader("🔥 En vedette")
        
        # --- TRI PAR POPULARITÉ ---
        # On vérifie si la colonne popularité existe
        pop_col = 'tmdb_popularity'
        
        if pop_col in df_actors.columns:
            # On convertit en numérique pour être sûr du tri
            df_actors[pop_col] = pd.to_numeric(df_actors[pop_col], errors='coerce').fillna(0)
            # On prend les 12 plus grands scores
            top_actors = df_actors.sort_values(by=pop_col, ascending=False).head(12)
        else:
            # Fallback si pas de colonne popularité
            top_actors = df_actors.head(12)
            
        cols = st.columns(6)
        for i, (_, row) in enumerate(top_actors.iterrows()):
            with cols[i % 6]:
                # On utilise la nouvelle fonction get_profile_url qui gère l'image par défaut
                st.image(get_profile_url(row), use_container_width=True)
                
                # Nom de l'acteur
                name_val = row.get('person_name') or row.get('intervenant_primaryName')
                st.markdown(f"**{name_val}**")
                
                if st.button("VOIR", key=f"grid_{row['nconst']}", use_container_width=True):
                    st.session_state.selected_actor_id = row['nconst']
                    st.rerun()