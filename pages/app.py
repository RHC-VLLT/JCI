import streamlit as st
import pandas as pd
import config, backend, acteurs_module, films_module

# --- INITIALISATION ---
st.set_page_config(page_title="Just Creuse It", layout="wide", initial_sidebar_state="collapsed")
df_movie, df_people, df_link = backend.load_data()
reco_data = backend.build_recommender(df_movie)

st.session_state.update({'df_movie': df_movie, 'df_people': df_people, 'df_link': df_link, 'reco_data': reco_data})
config.inject_css()

if 'current_page' not in st.session_state: st.session_state.current_page = "ACCUEIL"
if 'show_all_recos' not in st.session_state: st.session_state.show_all_recos = False

# --- STYLE CSS RESPONSIVE (HACK POUR MOBILE) ---
st.markdown("""
    <style>
    @media (max-width: 768px) {
        .hero-text {
            font-size: 2rem !important;
            padding-right: 20px !important;
            text-align: center !important;
            align-items: center !important;
        }
        .hero-container {
            height: 300px !important;
            justify-content: center !important;
            padding-right: 0px !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER NAVIGATION ---
st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
c_logo, c_spacer, c_nav1, c_nav2 = st.columns([2.5, 1, 0.6, 0.6])

with c_logo:
    if st.button("JUST CREUSE IT", key="logo_home"):
        st.session_state.update({
            'current_page': "ACCUEIL", 
            'detail_tconst': None, 
            'detail_actor_id': None, 
            'show_all_recos': False
        })
        st.rerun()

with c_nav1:
    if st.button("FILMS", type="secondary", use_container_width=True):
        st.session_state.update({'current_page': "FILMS", 'detail_tconst': None})
        st.rerun()

with c_nav2:
    if st.button("ACTEURS", type="secondary", use_container_width=True):
        st.session_state.update({'current_page': "ACTEURS", 'detail_actor_id': None})
        st.rerun()

st.markdown('<hr style="margin-top:0; border-top: 1px solid rgba(255,255,255,0.05);">', unsafe_allow_html=True)

# --- ROUTAGE ---
if st.session_state.current_page == "ACTEURS": 
    acteurs_module.show_acteurs()
elif st.session_state.current_page == "FILMS": 
    films_module.show_films()
else:
    # --- PAGE D'ACCUEIL ---
    hero_img_64 = config.load_base64_image(config.BG_PATH)
    if hero_img_64:
        st.markdown(f'''
            <div class="hero-container" style="background-image: linear-gradient(rgba(0,0,0,0.3), rgba(0,0,0,0.3)), url('data:image/jpeg;base64,{hero_img_64}'); 
                        height:400px; background-size:cover; background-position:center; 
                        border-radius:20px; border: 1px solid rgba(255,255,255,0.1); 
                        margin-bottom:40px; display:flex; flex-direction:column; 
                        align-items:flex-end; justify-content:center; padding-right:60px; color:white;">
                <h1 class="hero-text" style="font-size:3.5rem; font-weight:900; text-align:right; line-height:1.1; color: white !important; text-shadow: 2px 2px 15px rgba(0,0,0,0.6);">
                    LE CINÉMA QUI FAIT<br>BATTRE LE CŒUR<br>CREUSOIS
                </h1>
            </div>
        ''', unsafe_allow_html=True)

    # --- SÉLECTION FILTRÉE : FILM FRANÇAIS (SANS ANIMATION) ---
    df_fr = df_movie[
        (df_movie['production_1_countries_name'] == "France") & 
        (~df_movie['movie_genres_y'].str.contains("Animation", na=False))
    ]
    
    if df_fr.empty:
        df_fr = df_movie[~df_movie['movie_genres_y'].str.contains("Animation", na=False)]
    
    featured_movie = df_fr.sort_values(by='movie_release_date', ascending=False).iloc[0]
    
    st.markdown("<h3 style='color:#D7001D; text-transform:uppercase; letter-spacing:3px; margin-bottom:20px; font-size:1.1rem;'>À L'AFFICHE</h3>", unsafe_allow_html=True)
    
    # --- SECTION FOCUS ---
    col_v, col_i = st.columns([2.2, 1], gap="medium")
    
    with col_v:
        tr = featured_movie.get('trailer_url_fr') or featured_movie.get('youtube_url')
        if pd.notna(tr):
            v_id = str(tr).split('v=')[-1].split('&')[0] if 'v=' in str(tr) else str(tr).split('/')[-1].split('?')[0]
            st.markdown(f'''
                <div style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; border-radius: 15px; box-shadow: 0 15px 35px rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.05);">
                    <iframe style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border:0;" 
                    src="https://www.youtube.com/embed/{v_id}?autoplay=1&mute=1&loop=1&playlist={v_id}&rel=0" allow="autoplay; encrypted-media" allowfullscreen></iframe>
                </div>
            ''', unsafe_allow_html=True)

    with col_i:
        st.markdown(f'''
            <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-top-left-radius: 15px; border-top-right-radius: 15px; padding: 35px 25px; height: 465px; display: flex; flex-direction: column; justify-content: space-between;">
                <div>
                    <h2 style="color:white; margin:0; font-size:1.8rem; line-height:1.1; letter-spacing:-0.5px;">{featured_movie['display_title'].upper()}</h2>
                    <div style="display: flex; gap: 8px; margin-top: 15px; margin-bottom: 20px;">
                        <span style="background: #D7001D; color: white; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem; font-weight: 700; letter-spacing: 0.5px;">{featured_movie['production_1_countries_name'].upper()}</span>
                        <span style="background: rgba(255,255,255,0.08); color: #AAA; padding: 4px 12px; border-radius: 4px; font-size: 0.75rem;">{str(featured_movie['movie_release_date'])[:4]}</span>
                    </div>
                </div>
                <div style="display: flex; align-items: flex-start; gap: 18px; flex-grow: 1;">
                    <img src="{featured_movie.get('movie_poster_url_fr')}" style="width: 110px; border-radius: 8px; flex-shrink: 0; box-shadow: 0 8px 20px rgba(0,0,0,0.5);">
                    <div style="flex: 1; overflow: hidden;">
                        <p style="color: #BBB; font-size: 0.9rem; line-height: 1.6; margin: 0; font-style: italic; opacity: 0.9;">
                            "{str(featured_movie.get('movie_overview_fr', ''))[:250]}..."
                        </p>
                    </div>
                </div>
            </div>
        ''', unsafe_allow_html=True)
        
        if st.button("DÉCOUVRIR CE FILM", key="featured_go", type="primary", use_container_width=True):
            st.session_state.update({'detail_tconst': featured_movie['tconst'], 'current_page': "FILMS"})
            st.rerun()

    st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)

    # --- SECTION RECOMMANDATIONS ---
    st.markdown("<h2 style='text-align:center;'>VOS RECOMMANDATIONS</h2>", unsafe_allow_html=True)
    sel = st.selectbox("Basé sur un film que vous aimez :", sorted(df_movie['display_title'].unique()), index=None, key="home_sel_box")
    
    if sel:
        recos = backend.recommend_movies(sel, df_movie, reco_data)
        top_5 = recos[:5]
        others = recos[5:]

        st.markdown("<h4 style='color:#D7001D;'>TOP 5 DES MEILLEURES CORRESPONDANCES</h4>", unsafe_allow_html=True)
        cols_top = st.columns(5)
        for i, f in enumerate(top_5):
            with cols_top[i]:
                st.markdown(f'''<div class="movie-card-container"><img src="{f['poster_url']}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"reco_{f['tconst']}", type="primary", use_container_width=True):
                    st.session_state.update({'detail_tconst': f['tconst'], 'current_page': "FILMS"})
                    st.rerun()

        if not st.session_state.show_all_recos and len(others) > 0:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("VOIR TOUTES LES AUTRES SUGGESTIONS ↓", use_container_width=True):
                st.session_state.show_all_recos = True
                st.rerun()

        if st.session_state.show_all_recos:
            st.markdown("<br><h4 style='color:#888;'>AUTRES SUGGESTIONS</h4>", unsafe_allow_html=True)
            for row_idx in range(0, len(others), 5):
                row_items = others[row_idx : row_idx + 5]
                grid_cols = st.columns(5)
                for i, f in enumerate(row_items):
                    with grid_cols[i]:
                        st.markdown(f'''<div class="movie-card-container"><img src="{f['poster_url']}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                        if st.button("DÉTAILS", key=f"reco_other_{f['tconst']}", type="primary", use_container_width=True):
                            st.session_state.update({'detail_tconst': f['tconst'], 'current_page': "FILMS"})
                            st.rerun()
            
            if st.button("RÉDUIRE ↑", use_container_width=True):
                st.session_state.show_all_recos = False
                st.rerun()