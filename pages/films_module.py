import streamlit as st
import pandas as pd
import math
from utils import get_poster_url
import backend

DEFAULT_USER_IMG = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

def show_films():
    df_movie = st.session_state.get('df_movie')
    df_people = st.session_state.get('df_people')
    df_link = st.session_state.get('df_link')
    detail_id = st.session_state.get('detail_tconst')

    if detail_id:
        m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
        reals, casting = backend.get_movie_cast_info(m['tconst'], df_link, df_people)
        
        if st.button("⬅ RETOUR"):
            st.session_state.detail_tconst = None
            st.rerun()

        col1, col2 = st.columns([1, 2], gap="large")
        with col1: 
            st.image(get_poster_url(m), use_container_width=True)
        with col2:
            st.markdown(f"<h1 style='color:#D7001D; font-size:3.5rem; margin-bottom:0;'>{m['display_title'].upper()}</h1>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-weight:700; color:#888;'>{int(m['movie_startYear'])} • {m['movie_genres_y']}</p>", unsafe_allow_html=True)
            st.markdown(f'<div style="border-left:4px solid #D7001D; padding-left:15px; font-style:italic; margin-bottom:20px;">"{m.get("movie_overview_fr") or m.get("movie_overview") or "Pas de résumé disponible."}"</div>', unsafe_allow_html=True)
            
            st.write(f"**Réalisation :** {', '.join(reals)}")
            
            # --- NOUVEAU VISUEL CASTING ---
            st.markdown("<br><h3 style='color:#D7001D; text-transform:uppercase;'>Casting</h3>", unsafe_allow_html=True)
            c_cols = st.columns(4) # 4 colonnes pour que ce soit plus gros
            for i, act in enumerate(casting[:8]): # On en affiche jusqu'à 8
                with c_cols[i % 4]:
                    pic = act.get('photo')
                    pic = pic if pd.notna(pic) and str(pic).lower() not in ["nan", ""] else DEFAULT_USER_IMG
                    
                    # Rendu HTML de la carte
                    st.markdown(f'''
                        <div class="cast-card">
                            <img src="{pic}" class="cast-img">
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    # Bouton pour le profil (sécurisé)
                    act_id = act.get('nconst') or act.get('nconst_x') or act.get('nconst_y')
                    if act_id:
                        if st.button(act.get("name", "Inconnu"), key=f"c_{act_id}_{i}", use_container_width=True):
                            st.session_state.detail_actor_id = act_id
                            st.session_state.current_page = "ACTEURS"
                            st.rerun()

        # SECTION TRAILER
        tr = m.get('trailer_url_fr') or m.get('youtube_url')
        if pd.notna(tr) and "http" in str(tr):
            st.markdown("---")
            st.video(tr)

    else:
        # Grille catalogue standard
        st.markdown("<h1 style='text-align:center;'>BIBLIOTHÈQUE</h1>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        with c1: search = st.text_input("Titre", placeholder="Chercher un film...", label_visibility="collapsed", key="search_f")
        with c2: 
            genres = sorted(list(set([g.strip() for sl in df_movie['movie_genres_y'].dropna().str.split(',') for g in sl])))
            genre = st.selectbox("Genre", ["Tous les genres"] + genres, label_visibility="collapsed")

        df_f = df_movie.copy()
        if search: df_f = df_f[df_f['display_title'].str.contains(search, case=False, na=False)]
        if genre != "Tous les genres": df_f = df_f[df_f['movie_genres_y'].str.contains(genre, na=False)]

        limit = 20
        p = st.number_input("Page", min_value=1, max_value=math.ceil(len(df_f)/limit) or 1, step=1)
        grid = st.columns(5)
        for idx, (_, row) in enumerate(df_f.iloc[(p-1)*limit : p*limit].iterrows()):
            with grid[idx % 5]:
                st.markdown(f'''<div class="movie-card-container"><img src="{get_poster_url(row)}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"f_{row['tconst']}", type="primary", use_container_width=True):
                    st.session_state.detail_tconst = row['tconst']
                    st.rerun()