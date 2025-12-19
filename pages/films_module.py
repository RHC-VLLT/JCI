import streamlit as st
import pandas as pd
import math
from utils import get_poster_url
import backend

DEFAULT_USER_IMG = "https://cdn-icons-png.flaticon.com/512/149/149071.png"
DEFAULT_MOVIE_POSTER = "https://via.placeholder.com/600x900?text=Affiche+Indisponible"

# Dictionnaire de traduction des genres
GENRE_TRADUCTION = {
    "Action": "Action", "Adventure": "Aventure", "Animation": "Animation",
    "Biography": "Biographie", "Comedy": "Comédie", "Crime": "Crime",
    "Documentary": "Documentaire", "Drama": "Drame", "Family": "Famille",
    "Fantasy": "Fantastique", "History": "Histoire", "Horror": "Horreur",
    "Music": "Musique", "Musical": "Comédie musicale", "Mystery": "Mystère",
    "Romance": "Romance", "Sci-Fi": "Science-Fiction", "Sport": "Sport",
    "Thriller": "Thriller", "War": "Guerre", "Western": "Western"
}

def show_films():
    """Fonction principale appelée par app.py pour afficher la bibliothèque ou les détails."""
    df_movie = st.session_state.get('df_movie')
    df_people = st.session_state.get('df_people')
    df_link = st.session_state.get('df_link')
    detail_id = st.session_state.get('detail_tconst')

    if detail_id:
        # --- FORCER LE SCROLL EN HAUT AU CHARGEMENT DES DÉTAILS ---
        st.components.v1.html(
            """
            <script>
                window.parent.document.querySelector('.stApp').scrollTo(0, 0);
            </script>
            """,
            height=0,
        )

        # --- VUE DÉTAILLÉE DU FILM ---
        m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
        reals, casting = backend.get_movie_cast_info(m['tconst'], df_link, df_people)
        
        if st.button("⬅ RETOUR"):
            st.session_state.detail_tconst = None
            st.rerun()

        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1: 
            poster_url = get_poster_url(m)
            if not poster_url or pd.isna(poster_url) or str(poster_url).strip() == "":
                poster_url = DEFAULT_MOVIE_POSTER
            
            st.image(poster_url, use_container_width=True)
            
            # --- AFFICHAGE DE LA NOTE ---
            note = m.get('movie_vote_average_tmdb')
            if pd.notna(note) and note != 0:
                st.markdown(f"""
                    <div style="background-color:#D7001D; border-radius:10px; padding:15px; text-align:center; margin-top:15px;">
                        <span style="font-size:1.4rem; font-weight:900; color:white; text-transform: uppercase;">
                            NOTE : {note}/10
                        </span>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"<h1 style='color:#D7001D; font-size:3.5rem; margin-bottom:0;'>{m['display_title'].upper()}</h1>", unsafe_allow_html=True)
            
            pays_val = m.get('production_1_countries_name')
            pays_str = f" • {pays_val}" if pd.notna(pays_val) and str(pays_val).strip() != "" else ""
            
            genres_raw = str(m.get('movie_genres_y', '')).split(',')
            genres_traduits = [GENRE_TRADUCTION.get(g.strip(), g.strip()) for g in genres_raw]
            genres_str = ", ".join(genres_traduits)

            st.markdown(f"""
                <p style='font-weight:700; color:white !important; font-size:1.2rem; margin-top:0;'>
                    {int(m['movie_startYear'])} • {genres_str}{pays_str}
                </p>
            """, unsafe_allow_html=True)
            
            st.markdown(f'''<div style="border-left:4px solid #D7001D; padding-left:15px; font-style:italic; margin-bottom:20px; font-size:1.1rem; color:white;">"{m.get("movie_overview_fr") or m.get("movie_overview") or "Résumé non disponible."}"</div>''', unsafe_allow_html=True)
            
            st.markdown(f"<p style='color:white;'><strong>Réalisation :</strong> {', '.join(reals)}</p>", unsafe_allow_html=True)
            
            # --- SECTION CASTING ---
            st.markdown("<br><h3 style='color:#D7001D; text-transform:uppercase;'>Casting</h3>", unsafe_allow_html=True)
            c_cols = st.columns(4) 
            for i, act in enumerate(casting[:8]):
                with c_cols[i % 4]:
                    pic = act.get('photo')
                    if not pic or pd.isna(pic) or str(pic).strip() == "" or str(pic).lower() == "nan":
                        pic = DEFAULT_USER_IMG
                    
                    nom_acteur = act.get("name", "Inconnu")
                    
                    st.markdown(f'''
                        <div style="text-align:center; margin-bottom:10px;">
                            <img src="{pic}" style="width:85px; height:85px; object-fit:cover; border-radius:50%; border:2px solid #D7001D; margin-bottom:5px;">
                            <p style="color:white; font-size:0.9rem; font-weight:bold; margin:0; line-height:1.1;">{nom_acteur}</p>
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    act_id = act.get('nconst') or act.get('nconst_x')
                    if act_id:
                        if st.button("Voir fiche", key=f"c_{act_id}_{i}", use_container_width=True):
                            st.session_state.detail_actor_id = act_id
                            st.session_state.current_page = "ACTEURS"
                            st.rerun()

        tr = m.get('trailer_url_fr') or m.get('youtube_url')
        if pd.notna(tr) and "http" in str(tr):
            st.markdown("<br><hr style='border-top: 1px solid rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#D7001D; text-transform:uppercase; text-align:center;'>Bande-Annonce Officielle</h3>", unsafe_allow_html=True)
            
            v_col1, v_col2, v_col3 = st.columns([0.1, 0.8, 0.1])
            with v_col2:
                st.video(tr)

    else:
        # --- VUE BIBLIOTHÈQUE ---
        st.markdown("<h1 style='text-align:center; color:white;'>BIBLIOTHÈQUE</h1>", unsafe_allow_html=True)
        
        # --- TITRES AU-DESSUS DES FILTRES (AVEC MARGIN-BOTTOM 10PX) ---
        c_search, c_genre, c_page = st.columns([1.2, 1.8, 0.8])
        
        with c_search:
            st.markdown("<p style='color:#D7001D; font-weight:bold; margin-bottom:10px;'>RECHERCHE TITRE</p>", unsafe_allow_html=True)
            all_movie_names = sorted(df_movie['display_title'].dropna().unique().tolist())
            
            def on_movie_search_change():
                if st.session_state.movie_search_key:
                    found = df_movie[df_movie['display_title'] == st.session_state.movie_search_key]
                    if not found.empty:
                        st.session_state.detail_tconst = found.iloc[0].get('tconst')

            st.selectbox(
                "Chercher un film", 
                options=[""] + all_movie_names, 
                index=0, 
                key="movie_search_key", 
                on_change=on_movie_search_change, 
                label_visibility="collapsed"
            )
        
        with c_genre:
            st.markdown("<p style='color:#D7001D; font-weight:bold; margin-bottom:10px;'>FILTRER PAR GENRES</p>", unsafe_allow_html=True)
            genres_en = sorted(list(set([g.strip() for sl in df_movie['movie_genres_y'].dropna().str.split(',') for g in sl])))
            genres_fr_dispo = sorted([GENRE_TRADUCTION.get(g, g) for g in genres_en])
            
            genres_selectionnes_fr = st.multiselect(
                "Genres", 
                options=genres_fr_dispo, 
                default=[], 
                placeholder="Choisir des genres",
                label_visibility="collapsed"
            )

        # Calcul du filtrage
        df_f = df_movie.copy()
        if genres_selectionnes_fr:
            for genre_fr in genres_selectionnes_fr:
                genre_en_cible = [en for en, fr in GENRE_TRADUCTION.items() if fr == genre_fr]
                if genre_en_cible:
                    df_f = df_f[df_f['movie_genres_y'].str.contains(genre_en_cible[0], na=False)]

        limit = 20
        total_p = math.ceil(len(df_f)/limit) or 1

        with c_page:
            st.markdown("<p style='color:#D7001D; font-weight:bold; margin-bottom:10px;'>PAGE</p>", unsafe_allow_html=True)
            p = st.number_input("Page", min_value=1, max_value=total_p, step=1, label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        
        # --- GRILLE DE FILMS ---
        grid = st.columns(5)
        start_idx = (p - 1) * limit
        end_idx = p * limit
        
        for idx, (_, row) in enumerate(df_f.iloc[start_idx:end_idx].iterrows()):
            with grid[idx % 5]:
                p_url = get_poster_url(row)
                if not p_url or pd.isna(p_url) or str(p_url).strip() == "":
                    p_url = DEFAULT_MOVIE_POSTER
                
                st.markdown(f'''<div class="movie-card-container"><img src="{p_url}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"f_{row['tconst']}", type="primary", use_container_width=True):
                    st.session_state.detail_tconst = row['tconst']
                    st.rerun()