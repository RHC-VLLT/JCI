import streamlit as st
import pandas as pd
import config
import backend
from utils import get_poster_url

st.set_page_config(page_title="Just Creuse It - Cinéma", layout="wide", initial_sidebar_state="collapsed")

# CHARGEMENT ASSETS ET DONNEES
logo_b64 = config.load_base64_image(config.LOGO_PATH)
logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
bg_banner_b64 = config.load_base64_image(config.BG_PATH)
config.inject_css()

df_movie, df_people, df_link = backend.load_data()
recommender_data = backend.build_recommender(df_movie)

# ETAT
if 'recommended_films' not in st.session_state:
    st.session_state['recommended_films'] = None
    st.session_state['last_search_title'] = ""
    st.session_state['detail_tconst'] = None
    st.session_state['show_all_recos'] = False

detail_id = st.session_state.get('detail_tconst')

if not detail_id:
    # --- NAVIGATION ---
    c_logo, c_nav, c_spacer = st.columns([1, 3, 1])
    with c_logo:
        if logo_url: st.markdown(f'<img src="{logo_url}" width="70%">', unsafe_allow_html=True)
    with c_nav:
        st.markdown('<div class="modern-navbar-container"><a href="#" class="active">Accueil</a><a href="#">Films</a><a href="#">Acteurs</a></div>', unsafe_allow_html=True)

    # --- HERO BANNER ---
    bg_style = f"background-image: url('data:image/jpeg;base64,{bg_banner_b64}');" if bg_banner_b64 else ""
    st.markdown(f'<div class="hero"><div class="hero-overlay"></div><div class="hero-content"><div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div><a href="#recherche" class="btn-main">Découvrir</a></div></div><div id="recherche"></div>', unsafe_allow_html=True)

    # --- RECHERCHE ---
    st.markdown("<h1 style='text-align:center;margin:50px 0;'>TROUVEZ VOTRE FILM</h1>", unsafe_allow_html=True)
    sel_movie = st.selectbox("Recherche", sorted(df_movie['display_title'].unique().tolist()), index=None, label_visibility="collapsed")
    
    if sel_movie and sel_movie != st.session_state.get('last_search_title'):
        recos, _ = backend.recommend_movies(sel_movie, df_movie, recommender_data)
        st.session_state['recommended_films'] = recos
        st.session_state['last_search_title'] = sel_movie

    # --- GRILLE ---
    recos = st.session_state.get('recommended_films')
    if recos:
        filtered = [f for f in recos if f['score_sim'] > 50]
        st.markdown("<h2 style='text-align:center;margin:40px 0;'>RECOMMANDATIONS</h2>", unsafe_allow_html=True)
        cols = st.columns(5)
        for i, film in enumerate(filtered[:10]):
            with cols[i % 5]:
                poster = film.get("poster_url", "")
                st.markdown(f'''<div class="movie-card-xl"><div style="height:550px;position:relative;"><div style="position:absolute;top:20px;right:20px;background:#D7001D;padding:5px 15px;border-radius:6px;font-weight:900;">{film['score_sim']:.0f}%</div><img src="{poster}" style="width:100%;height:100%;object-fit:cover;"></div><div style="padding:15px;text-align:center;"><b>{film['titre'].upper()}</b><br><span style="color:#D7001D">{film['annee']} • {film['genres'].split(',')[0].upper()}</span></div></div>''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"btn_{film['tconst']}_{i}"):
                    st.session_state['detail_tconst'] = film['tconst']
                    st.rerun()
else:
    # --- FICHE DÉTAIL (STYLE THE DIRT) ---
    m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
    ids = df_link[df_link['tconst'] == detail_id]['nconst'].tolist()
    peoples = df_people[df_people['nconst'].isin(ids)]
    reals = peoples[peoples['person_professions'].str.contains('director', na=False)]['person_name'].tolist()
    acts = peoples[peoples['person_professions'].str.contains('actor|actress', na=False)]['person_name'].head(5).tolist()

    if st.button("⬅ RETOUR"): st.session_state['detail_tconst'] = None; st.rerun()

    c1, c2 = st.columns([1, 2])
    with c1: st.image(get_poster_url(m), use_container_width=True)
    with c2:
        st.markdown(f'<h1 style="font-size:4rem;font-weight:900;margin:0;">{m["display_title"].upper()}</h1>', unsafe_allow_html=True)
        st.markdown(f'<p style="color:#D7001D;font-weight:700;font-size:1.2rem;">{int(m["movie_startYear"])} • {int(m["movie_runtimeMinutes"])} MIN</p>', unsafe_allow_html=True)
        st.markdown(f'<div style="border-left:4px solid #D7001D;padding-left:20px;margin:30px 0;font-style:italic;color:#CCC;">"{m.get("movie_overview_fr") or m.get("movie_overview")}"</div>', unsafe_allow_html=True)
        ca1, ca2 = st.columns(2)
        with ca1: st.markdown(f'<b>RÉALISATION</b><br>{", ".join(reals)}', unsafe_allow_html=True)
        with ca2: st.markdown(f'<b>CASTING</b><br>{", ".join(acts)}', unsafe_allow_html=True)