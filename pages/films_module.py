import streamlit as st
import pandas as pd
import math
from utils import get_poster_url
import backend

def show_films():
    """Affiche la bibliothèque de films avec recherche, filtres et style harmonisé."""
    df_movie = st.session_state.get('df_movie')
    df_people = st.session_state.get('df_people')
    df_link = st.session_state.get('df_link')
    
    detail_id = st.session_state.get('detail_tconst')

    # --- LOGIQUE : VUE DÉTAILLÉE ---
    if detail_id:
        m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
        reals, casting = backend.get_movie_cast_info(m['tconst'], df_link, df_people)
        
        if st.button("⬅ RETOUR À LA LISTE"):
            st.session_state.detail_tconst = None
            st.rerun()

        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(get_poster_url(m), use_container_width=True)
        with col2:
            st.markdown(f"<h1 style='color:#D7001D; font-size:3rem;'>{m['display_title'].upper()}</h1>", unsafe_allow_html=True)
            st.write(f"**Année :** {int(m['movie_startYear'])} | **Genres :** {m['movie_genres_y']}")
            st.markdown(f'<div style="border-left:4px solid #D7001D; padding-left:15px; font-style:italic;">"{m.get("movie_overview_fr") or m.get("movie_overview")}"</div>', unsafe_allow_html=True)
            
            st.write("### Casting principal")
            c_cols = st.columns(5)
            for i, actor in enumerate(casting[:5]):
                with c_cols[i]:
                    pic = actor['photo'] if pd.notna(actor['photo']) else "https://via.placeholder.com/150"
                    st.markdown(f'<div style="text-align:center;"><img src="{pic}" style="width:70px;height:70px;border-radius:50%;object-fit:cover;border:2px solid #D7001D;"><p style="font-size:0.7rem;">{actor["name"]}</p></div>', unsafe_allow_html=True)

    # --- LOGIQUE : CATALOGUE (GRILLE) ---
    else:
        st.markdown("<h1 style='text-align:center;'>BIBLIOTHÈQUE DE FILMS</h1>", unsafe_allow_html=True)
        
        # ZONE DE FILTRES
        c1, c2 = st.columns([3, 1])
        with c1:
            search = st.text_input("Rechercher", placeholder="Sacé sur un filme...", label_visibility="collapsed")
        with c2:
            all_genres = sorted(list(set([g.strip() for sublist in df_movie['movie_genres_y'].dropna().str.split(',') for g in sublist])))
            genre = st.selectbox("Genre", ["Tous les genres"] + all_genres, label_visibility="collapsed")

        # FILTRAGE
        df_f = df_movie.copy()
        if search:
            df_f = df_f[df_f['display_title'].str.contains(search, case=False, na=False)]
        if genre != "Tous les genres":
            df_f = df_f[df_f['movie_genres_y'].str.contains(genre, na=False)]

        # PAGINATION
        limit = 20
        pages = math.ceil(len(df_f) / limit)
        
        if pages > 0:
            p = st.number_input("Page", min_value=1, max_value=pages, step=1, label_visibility="collapsed")
            start = (p - 1) * limit
            
            # AFFICHAGE DE LA GRILLE (Style Shrek/Aladdin)
            grid = st.columns(5)
            for idx, (_, row) in enumerate(df_f.iloc[start : start+limit].iterrows()):
                with grid[idx % 5]:
                    # Conteneur Image
                    st.markdown(f'''
                        <div class="movie-card-container">
                            <img src="{get_poster_url(row)}" class="movie-poster-img">
                        </div>
                    ''', unsafe_allow_html=True)
                    
                    # Bouton DÉTAILS (Le CSS kind="primary" se charge de le coller)
                    if st.button("DÉTAILS", key=f"btn_{row['tconst']}", type="primary", use_container_width=True):
                        st.session_state.detail_tconst = row['tconst']
                        st.rerun()
        else:
            st.error("Aucun film trouvé.")