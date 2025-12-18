import streamlit as st
import pandas as pd
import math
from utils import get_poster_url
import backend

DEFAULT_USER_IMG = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

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
    df_movie = st.session_state.get('df_movie')
    df_people = st.session_state.get('df_people')
    df_link = st.session_state.get('df_link')
    detail_id = st.session_state.get('detail_tconst')

    if detail_id:
        # --- VUE DÉTAILLÉE DU FILM ---
        m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
        reals, casting = backend.get_movie_cast_info(m['tconst'], df_link, df_people)
        
        if st.button("⬅ RETOUR"):
            st.session_state.detail_tconst = None
            st.rerun()

        # Layout principal : Affiche à gauche, Infos à droite
        col1, col2 = st.columns([1, 2], gap="large")
        
        with col1: 
            st.image(get_poster_url(m), use_container_width=True)
            
            # --- AFFICHAGE DE LA NOTE (Badge Rouge) ---
            note = m.get('movie_averageRating') or m.get('averageRating')
            if pd.notna(note) and note != 0:
                st.markdown(f"""
                    <div style="background-color:#D7001D; border-radius:10px; padding:15px; text-align:center; margin-top:15px; border: 1px solid white;">
                        <span style="font-size:1.4rem; font-weight:900; color:white;">NOTE : {note}/10</span>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            # Titre
            st.markdown(f"<h1 style='color:#D7001D; font-size:3.5rem; margin-bottom:0;'>{m['display_title'].upper()}</h1>", unsafe_allow_html=True)
            
            # --- INFOS : ANNÉE • GENRES • PAYS ---
            pays_val = m.get('movie_country') or m.get('country')
            pays_str = f" • {pays_val}" if pd.notna(pays_val) and str(pays_val).strip() != "" else ""
            
            genres_raw = str(m.get('movie_genres_y', '')).split(',')
            genres_traduits = [GENRE_TRADUCTION.get(g.strip(), g.strip()) for g in genres_raw]
            genres_str = ", ".join(genres_traduits)

            st.markdown(f"""
                <p style='font-weight:700; color:white !important; font-size:1.2rem; margin-top:0;'>
                    {int(m['movie_startYear'])} • {genres_str}{pays_str}
                </p>
            """, unsafe_allow_html=True)
            
            # Synopsis
            st.markdown(f'''<div style="border-left:4px solid #D7001D; padding-left:15px; font-style:italic; margin-bottom:20px; font-size:1.1rem; color:white;">"{m.get("movie_overview_fr") or m.get("movie_overview") or "Résumé non disponible."}"</div>''', unsafe_allow_html=True)
            
            st.markdown(f"<p style='color:white;'><strong>Réalisation :</strong> {', '.join(reals)}</p>", unsafe_allow_html=True)
            
            # --- SECTION CASTING ---
            st.markdown("<br><h3 style='color:#D7001D; text-transform:uppercase;'>Casting</h3>", unsafe_allow_html=True)
            c_cols = st.columns(4) 
            for i, act in enumerate(casting[:8]):
                with c_cols[i % 4]:
                    pic = act.get('photo')
                    pic = pic if pd.notna(pic) and str(pic).lower() not in ["nan", ""] else DEFAULT_USER_IMG
                    st.markdown(f'''<div class="cast-container"><img src="{pic}" class="cast-img"></div>''', unsafe_allow_html=True)
                    
                    act_id = act.get('nconst') or act.get('nconst_x')
                    if act_id:
                        if st.button(act.get("name", "Inconnu"), key=f"c_{act_id}_{i}", use_container_width=True):
                            st.session_state.detail_actor_id = act_id
                            st.session_state.current_page = "ACTEURS"
                            st.rerun()

        # --- SECTION BANDE-ANNONCE (LARGE, EN BAS DE PAGE) ---
        tr = m.get('trailer_url_fr') or m.get('youtube_url')
        if pd.notna(tr) and "http" in str(tr):
            st.markdown("<br><hr style='border-top: 1px solid rgba(255,255,255,0.1);'><br>", unsafe_allow_html=True)
            st.markdown("<h3 style='color:#D7001D; text-transform:uppercase; text-align:center;'>Bande-Annonce Officielle</h3>", unsafe_allow_html=True)
            
            # Conteneur centré pour la vidéo
            v_col1, v_col2, v_col3 = st.columns([0.1, 0.8, 0.1])
            with v_col2:
                st.video(tr)

    else:
        # --- VUE BIBLIOTHÈQUE ---
        st.markdown("<h1 style='text-align:center; color:white;'>BIBLIOTHÈQUE</h1>", unsafe_allow_html=True)
        c1, c2 = st.columns([3, 1])
        
        with c1: 
            search = st.text_input("Titre", placeholder="Chercher un film...", label_visibility="collapsed", key="search_f")
        
        with c2: 
            genres_en = sorted(list(set([g.strip() for sl in df_movie['movie_genres_y'].dropna().str.split(',') for g in sl])))
            genres_fr = ["Tous les genres"] + [GENRE_TRADUCTION.get(g, g) for g in genres_en]
            genre_selectionne_fr = st.selectbox("Genre", genres_fr, label_visibility="collapsed")

        df_f = df_movie.copy()
        if search: 
            df_f = df_f[df_f['display_title'].str.contains(search, case=False, na=False)]
        
        if genre_selectionne_fr != "Tous les genres":
            genre_en_cible = [en for en, fr in GENRE_TRADUCTION.items() if fr == genre_selectionne_fr]
            if genre_en_cible:
                df_f = df_f[df_f['movie_genres_y'].str.contains(genre_en_cible[0], na=False)]

        limit = 20
        total_p = math.ceil(len(df_f)/limit) or 1
        p = st.number_input("Page", min_value=1, max_value=total_p, step=1)
        
        grid = st.columns(5)
        for idx, (_, row) in enumerate(df_f.iloc[(p-1)*limit : p*limit].iterrows()):
            with grid[idx % 5]:
                st.markdown(f'''<div class="movie-card-container"><img src="{get_poster_url(row)}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"f_{row['tconst']}", type="primary", use_container_width=True):
                    st.session_state.detail_tconst = row['tconst']
                    st.rerun()