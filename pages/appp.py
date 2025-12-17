import streamlit as st
import config, backend, acteurs_module, films_module

st.set_page_config(page_title="Just Creuse It", layout="wide", initial_sidebar_state="collapsed")
df_movie, df_people, df_link = backend.load_data()
reco_data = backend.build_recommender(df_movie)

st.session_state.update({'df_movie': df_movie, 'df_people': df_people, 'df_link': df_link, 'reco_data': reco_data})
config.inject_css()

if 'current_page' not in st.session_state: st.session_state.current_page = "ACCUEIL"

st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
c_logo, c_nav1, c_nav2 = st.columns([2, 1, 1])
with c_logo:
    if st.button("🔴 JUST CREUSE IT", type="secondary"):
        st.session_state.update({'current_page': "ACCUEIL", 'detail_tconst': None, 'detail_actor_id': None})
        st.rerun()
with c_nav1:
    if st.button("🎬 FILMS", type="secondary", use_container_width=True):
        st.session_state.update({'current_page': "FILMS", 'detail_tconst': None})
        st.rerun()
with c_nav2:
    if st.button("🎭 ACTEURS", type="secondary", use_container_width=True):
        st.session_state.update({'current_page': "ACTEURS", 'detail_actor_id': None})
        st.rerun()

st.markdown("---")

if st.session_state.current_page == "ACTEURS": acteurs_module.show_acteurs()
elif st.session_state.current_page == "FILMS": films_module.show_films()
else:
    bg_64 = config.load_base64_image(config.BG_PATH)
    bg_style = f"background-image: url('data:image/jpeg;base64,{bg_64}');" if bg_64 else ""
    st.markdown(f'''<div class="hero" style="{bg_style}"><div class="hero-title">LE CINÉMA<br>SANS LIMITES</div></div>''', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center; margin-top:40px;'>✨ VOS RECOMMANDATIONS</h2>", unsafe_allow_html=True)
    sel = st.selectbox("Basé sur un film :", sorted(df_movie['display_title'].unique()), index=None, key="home_sel_box")
    if sel:
        recos = backend.recommend_movies(sel, df_movie, reco_data)
        cols = st.columns(5)
        for i, f in enumerate(recos):
            with cols[i % 5]:
                st.markdown(f'''<div class="movie-card-container"><img src="{f['poster_url']}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"reco_{f['tconst']}", type="primary", use_container_width=True):
                    st.session_state.update({'detail_tconst': f['tconst'], 'current_page': "FILMS"})
                    st.rerun()