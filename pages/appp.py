import streamlit as st
import pandas as pd
import config
import backend
# Import du nouveau module (qui est juste à côté)
import acteurs_module 
from utils import get_poster_url

# 1. CONFIGURATION
st.set_page_config(
    page_title="Just Creuse It - Cinéma",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Gestion de la navigation (SPA)
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 'home'

# ==============================================================================
# ROUTEUR (C'est lui qui décide quelle page afficher)
# ==============================================================================
if st.session_state['current_page'] == 'acteurs':
    # On injecte le CSS global
    config.inject_css() 
    # On lance la fonction du module acteurs
    acteurs_module.show_acteurs()
    
else:
    # >>> ICI COMMENCE LA PAGE D'ACCUEIL CLASSIQUE <<<
    
    # Chargement Assets
    logo_b64 = config.load_base64_image(config.LOGO_PATH)
    logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""
    bg_banner_b64 = config.load_base64_image(config.BG_PATH)
    config.inject_css()

    # Chargement Données
    df_movie, df_people, df_link = backend.load_data()
    recommender_data = backend.build_recommender(df_movie)

    # État
    if 'recommended_films' not in st.session_state:
        st.session_state['recommended_films'] = None
        st.session_state['last_search_title'] = ""
        st.session_state['detail_tconst'] = None
        st.session_state['show_all_recos'] = False

    # --- LOGIQUE D'AFFICHAGE ACCUEIL ---
    detail_id = st.session_state.get('detail_tconst')

    if not detail_id:
        # MODE ACCUEIL
        
        # NAVBAR
        c_logo, c_nav, c_btn = st.columns([1, 3, 1])
        with c_logo:
            if logo_url:
                st.markdown(f'<img src="{logo_url}" width="70%">', unsafe_allow_html=True)
            else:
                st.markdown("### JCI")
        
        with c_nav:
            st.markdown('<div class="modern-navbar-container"><a href="#" class="active">Accueil</a><a href="#">Films</a><a href="#">Genre</a></div>', unsafe_allow_html=True)
            
        with c_btn:
            # === LE BOUTON QUI CHANGE TOUT ===
            if st.button("🎭 ACTEURS", use_container_width=True):
                st.session_state['current_page'] = 'acteurs'
                st.rerun()
            # =================================

        # HERO BANNIERE
        bg_style = f"background-image: url('data:image/jpeg;base64,{bg_banner_b64}');" if bg_banner_b64 else f"background-image: url('{config.SITE_BG_URL}');"
        st.markdown(f"""
        <div class="hero" style="{bg_style}">
            <div class="hero-overlay"></div>
            <div class="hero-content">
                <div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div>
                <a href="#recherche" class="btn-main">Découvrir</a>
            </div>
        </div><div id='recherche'></div>
        """, unsafe_allow_html=True)

        # RECHERCHE FILM
        st.markdown("<div style='text-align:center;margin:50px 0;'><h1 style='font-size:2.8rem;'>TROUVEZ VOTRE FILM</h1></div>", unsafe_allow_html=True)
        sel_movie = st.selectbox("Recherche", sorted(df_movie['display_title'].unique().tolist()), index=None, label_visibility="collapsed")
        
        if sel_movie and sel_movie != st.session_state.get('last_search_title'):
             recos, _ = backend.recommend_movies(sel_movie, df_movie, recommender_data)
             st.session_state['recommended_films'] = recos
             st.session_state['last_search_title'] = sel_movie

        # GRILLE RESULTATS
        recos = st.session_state.get('recommended_films')
        if recos:
            filtered = [f for f in recos if f['score_sim'] > 50]
            to_show = filtered if st.session_state.get('show_all_recos') else filtered[:5]
            
            if to_show:
                st.markdown(f"<h2 style='text-align:center;'>RECOMMANDATIONS</h2>", unsafe_allow_html=True)
                cols = st.columns(5)
                for i, film in enumerate(to_show):
                    with cols[i % 5]:
                        poster = film.get("poster_url", "")
                        st.markdown(f'''<div class="movie-card-xl"><img src="{poster}" style="width:100%"></div>''', unsafe_allow_html=True)
                        if st.button("DÉTAILS", key=f"btn_{film['tconst']}_{i}", use_container_width=True):
                            st.session_state['detail_tconst'] = film['tconst']
                            st.rerun()
                
                if not st.session_state.get('show_all_recos') and len(filtered) > 5:
                    if st.button("VOIR PLUS"):
                        st.session_state['show_all_recos'] = True
                        st.rerun()

    else:
        # MODE DETAIL FILM
        m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
        
        # Récup casting rapide
        ids = df_link[df_link['tconst'] == detail_id]['nconst'].tolist()
        casting = df_people[df_people['nconst'].isin(ids)]['person_name'].head(5).tolist()
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.image(get_poster_url(m), use_container_width=True)
        with c2:
            st.title(m['display_title'])
            st.markdown(f"**Casting:** {', '.join(casting)}")
            tr_url = m.get('trailer_url_fr') or m.get('youtube_url')
            if pd.notna(tr_url) and "http" in str(tr_url):
                st.video(tr_url)
            
            if st.button("RETOUR LISTE", use_container_width=True):
                st.session_state['detail_tconst'] = None
                st.rerun()