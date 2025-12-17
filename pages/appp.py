import streamlit as st
import pandas as pd
import config
import backend
from utils import get_poster_url

# 1. SETUP & DATA
st.set_page_config(page_title="Just Creuse It", layout="wide", initial_sidebar_state="collapsed")
df_movie, df_people, df_link = backend.load_data()
reco_data = backend.build_recommender(df_movie)
config.inject_css()

# Navigation State
if 'page' not in st.session_state: st.session_state['page'] = 'FILMS'
if 'detail_tconst' not in st.session_state: st.session_state['detail_tconst'] = None

# --- HEADER MODERNE ---
col_logo, col_nav = st.columns([2, 2])
with col_logo:
    st.markdown("<h2 style='color:#D7001D; font-weight:800; margin-top:10px;'>JUST CREUSE IT</h2>", unsafe_allow_html=True)
with col_nav:
    c1, c2 = st.columns(2)
    with c1:
        if st.button("FILMS", type="secondary", use_container_width=True):
            st.session_state['page'] = 'FILMS'
            st.session_state['detail_tconst'] = None
            st.rerun()
    with c2:
        if st.button("ACTEURS", type="secondary", use_container_width=True):
            st.session_state['page'] = 'ACTEURS'
            st.rerun()

st.markdown("---")

# --- ROUTEUR ---
if st.session_state['page'] == 'ACTEURS':
    st.title("🎭 LES ACTEURS")
    st.write("Retrouvez ici tous les intervenants du cinéma.")

elif st.session_state['detail_tconst'] is not None:
    # --- PAGE DÉTAILS (MODERNE AVEC TRAILER) ---
    m = df_movie[df_movie['tconst'] == st.session_state['detail_tconst']].iloc[0]
    reals, casting = backend.get_movie_cast_info(m['tconst'], df_link, df_people)
    
    if st.button("⬅ RETOUR", type="primary"):
        st.session_state['detail_tconst'] = None
        st.rerun()

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(get_poster_url(m), use_container_width=True)
    with col2:
        st.markdown(f"<h1 style='font-size:3.5rem; margin-bottom:0;'>{m['display_title'].upper()}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#D7001D; font-weight:700;'>{int(m['movie_startYear'])} • {m['movie_genres_y']}</p>", unsafe_allow_html=True)
        st.markdown(f'<div style="border-left:4px solid #D7001D; padding-left:15px; font-style:italic; margin: 20px 0;">{m.get("movie_overview_fr") or m.get("movie_overview")}</div>', unsafe_allow_html=True)
        
        ca1, ca2 = st.columns(2)
        with ca1: st.markdown(f'<b>RÉALISATION:</b><br>{", ".join(reals)}', unsafe_allow_html=True)
        with ca2:
            st.markdown("<b>CASTING PRINCIPAL:</b>", unsafe_allow_html=True)
            cast_cols = st.columns(5)
            for i, actor in enumerate(casting):
                with cast_cols[i]:
                    photo = actor['photo'] if pd.notna(actor['photo']) else "https://via.placeholder.com/150"
                    st.markdown(f'<div class="cast-bubble"><img src="{photo}" class="cast-img"><p style="font-size:0.8rem; font-weight:600;">{actor["name"]}</p></div>', unsafe_allow_html=True)
        
        # --- SECTION BANDE-ANNONCE ---
        tr_url = m.get('trailer_url_fr') or m.get('youtube_url')
        if pd.notna(tr_url):
            st.markdown("<br><h3>🎬 BANDE-ANNONCE</h3>", unsafe_allow_html=True)
            st.video(tr_url)

else:
    # --- PAGE CATALOGUE (FILMS) ---
    bg_64 = config.load_base64_image(config.BG_PATH)
    bg_style = f"background-image: url('data:image/jpeg;base64,{bg_64}');" if bg_64 else ""
    st.markdown(f'<div class="hero" style="{bg_style}"><div class="hero-title">LE CINÉMA QUI FAIT<br>BATTRE LE CŒUR<br>CREUSOIS</div></div>', unsafe_allow_html=True)
    
    st.markdown("<h1 style='text-align:center; margin-top:30px;'>TROUVEZ VOTRE FILM</h1>", unsafe_allow_html=True)
    sel = st.selectbox("Recherche", sorted(df_movie['display_title'].unique()), index=None, label_visibility="collapsed")
    
    if sel:
        recos = backend.recommend_movies(sel, df_movie, reco_data)
        st.markdown("### RECOMMANDATIONS")
        cols = st.columns(5)
        for i, f in enumerate(recos):
            with cols[i % 5]:
                genre_short = str(f.get('movie_genres_y', 'N/A')).split(',')[0].upper()
                st.markdown(f'''
                    <div class="movie-card-xl">
                        <div style="position:absolute; top:10px; right:10px; background:#D7001D; padding:2px 10px; border-radius:4px; font-weight:800; font-size:0.8rem; z-index:10;">{f['score_sim']:.0f}% MATCH</div>
                        <img src="{f['poster_url']}" style="width:100%; height:80%; object-fit:cover;">
                        <div style="text-align:center; padding:10px;">
                            <div style="font-weight:800; font-size:1rem; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">{f['display_title'].upper()}</div>
                            <div style="color:#D7001D; font-size:0.85rem; font-weight:700; margin-top:5px;">{int(f.get('movie_startYear', 0))} • {genre_short}</div>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"btn_{f['tconst']}", type="primary"):
                    st.session_state['detail_tconst'] = f['tconst']
                    st.rerun()