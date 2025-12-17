import streamlit as st
import config, backend, acteurs_module, films_module

# --- INITIALISATION ---
st.set_page_config(page_title="Just Creuse It", layout="wide", initial_sidebar_state="collapsed")
df_movie, df_people, df_link = backend.load_data()
reco_data = backend.build_recommender(df_movie)

st.session_state.update({'df_movie': df_movie, 'df_people': df_people, 'df_link': df_link, 'reco_data': reco_data})
config.inject_css()

if 'current_page' not in st.session_state: st.session_state.current_page = "ACCUEIL"
if 'show_all_recos' not in st.session_state: st.session_state.show_all_recos = False

# --- HEADER NAVIGATION ---
st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)
# Colonnes ajustées : Le logo prend de la place, les boutons nav sont à droite
c_logo, c_spacer, c_nav1, c_nav2 = st.columns([2.5, 1, 0.6, 0.6])

with c_logo:
    # LOGO TEXTUEL ROUGE CLIQUABLE
    if st.button("JUST CREUSE IT", key="logo_home"):
        st.session_state.update({
            'current_page': "ACCUEIL", 
            'detail_tconst': None, 
            'detail_actor_id': None, 
            'show_all_recos': False
        })
        st.rerun()

with c_nav1:
    if st.button(" FILMS", type="secondary", use_container_width=True):
        st.session_state.update({'current_page': "FILMS", 'detail_tconst': None})
        st.rerun()

with c_nav2:
    if st.button(" ACTEURS", type="secondary", use_container_width=True):
        st.session_state.update({'current_page': "ACTEURS", 'detail_actor_id': None})
        st.rerun()

st.markdown("---")

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
            <div style="background-image: url('data:image/jpeg;base64,{hero_img_64}'); 
                        height:450px; background-size:cover; background-position:center; 
                        border-radius:20px; border: 1px solid rgba(255,255,255,0.1); margin-bottom:40px;">
            </div>
        ''', unsafe_allow_html=True)
    
    st.markdown("<h2 style='text-align:center;'> VOS RECOMMANDATIONS</h2>", unsafe_allow_html=True)
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
            if st.button(f"VOIR TOUTES LES AUTRES SUGGESTIONS (+{len(others)} FILMS) ↓", use_container_width=True):
                st.session_state.show_all_recos = True
                st.rerun()

        if st.session_state.show_all_recos:
            st.markdown(f"<br><h4 style='color:#888;'>AUTRES SUGGESTIONS</h4>", unsafe_allow_html=True)
            grid_cols = st.columns(5)
            for i, f in enumerate(others):
                with grid_cols[i % 5]:
                    st.markdown(f'''<div class="movie-card-container"><img src="{f['poster_url']}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                    if st.button("DÉTAILS", key=f"reco_other_{f['tconst']}", type="primary", use_container_width=True):
                        st.session_state.update({'detail_tconst': f['tconst'], 'current_page': "FILMS"})
                        st.rerun()
            
            if st.button("RÉDUIRE ↑", use_container_width=True):
                st.session_state.show_all_recos = False
                st.rerun()