import streamlit as st
import pandas as pd
import config
import backend
from utils import get_poster_url

# 1. CONFIGURATION
st.set_page_config(
    page_title="Just Creuse It - Cinéma",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# CHARGEMENT ASSETS
# ==============================================================================
# Logo
logo_b64 = config.load_base64_image(config.LOGO_PATH)
logo_url = f"data:image/png;base64,{logo_b64}" if logo_b64 else ""

# ICI : Chargement de l'image PopCorn.jpg via le chemin défini dans config
bg_banner_b64 = config.load_base64_image(config.BG_PATH)

# Injection du CSS global
config.inject_css()

# 2. CHARGEMENT DONNÉES
df_movie, df_people, df_link = backend.load_data()
recommender_data = backend.build_recommender(df_movie)

# 3. GESTION ÉTAT
if 'recommended_films' not in st.session_state:
    st.session_state['recommended_films'] = None
    st.session_state['last_search_title'] = ""
    st.session_state['detail_tconst'] = None
    st.session_state['show_all_recos'] = False

# ==============================================================================
# 4. LOGIQUE D'AFFICHAGE
# ==============================================================================
detail_id = st.session_state.get('detail_tconst')

if not detail_id:
    # --- MODE ACCUEIL ---
    
    # Navbar
    col_logo, col_nav_center, col_spacer = st.columns([1, 3, 1])
    with col_logo:
        if logo_url:
            st.markdown(f'<div style="display:flex;align-items:center;height:100%;padding-left:2%;"><a href="#" onclick="window.location.reload();"><img src="{logo_url}" width="70%"></a></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="logo-text-backup">JUST CREUSE IT</div>', unsafe_allow_html=True)
            
    with col_nav_center:
        st.markdown('<div class="modern-navbar-container"><a href="#" class="active">Accueil</a><a href="#">Films</a><a href="#">Acteurs</a></div>', unsafe_allow_html=True)

    # --- SECTION HERO (BANNIERE) ---
    # Si l'image PopCorn a bien été chargée, on l'utilise
    if bg_banner_b64:
        bg_img_style = f"background-image: url('data:image/jpeg;base64,{bg_banner_b64}');"
    else:
        # Sinon (sécurité), on met l'image de la salle de cinéma
        bg_img_style = f"background-image: url('{config.SITE_BG_URL}');"
    
    st.markdown(f"""
    <div class="hero" style="{bg_img_style}">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-title">Le Cinéma qui fait<br>battre le cœur<br>Creusois</div>
            <a href="#recherche" class="btn-main">Découvrir</a>
        </div>
    </div><div id='recherche'></div>
    """, unsafe_allow_html=True)

    # Recherche
    st.markdown("<div style='text-align:center;margin:50px 0;'><h1 style='font-size:2.8rem;'>TROUVEZ VOTRE FILM</h1></div>", unsafe_allow_html=True)
    
    selected_movie = st.selectbox("Recherche", sorted(df_movie['display_title'].unique().tolist()), index=None, label_visibility="collapsed", placeholder="Chercher un film...")
    
    if selected_movie and selected_movie != st.session_state.get('last_search_title'):
        with st.spinner("Analyse en cours..."):
            recos, _ = backend.recommend_movies(selected_movie, df_movie, recommender_data)
            st.session_state['recommended_films'] = recos
            st.session_state['last_search_title'] = selected_movie
            st.session_state['show_all_recos'] = False

    # Grille de résultats
    all_recos = st.session_state.get('recommended_films')
    filtered = [f for f in all_recos if f['score_sim'] > 50.0] if all_recos else []
    
    if st.session_state.get('show_all_recos'):
        to_show = filtered
        cols_count = 4
        title = f"TOUS LES RÉSULTATS ({len(filtered)})"
    else:
        to_show = filtered[:5]
        cols_count = 5
        title = "TOP 5 RECOMMANDATIONS"

    if to_show:
        st.markdown(f"<h2 style='text-align:center;margin:40px 0;'>{title}</h2>", unsafe_allow_html=True)
        cols = st.columns(cols_count)
        for i, film in enumerate(to_show):
            with cols[i % cols_count]:
                poster = film.get("poster_url", "")
                card = f'''<div class="movie-card-xl"><div style="height:550px;overflow:hidden;"><img src="{poster}" style="width:100%;height:100%;object-fit:cover;"></div>
                           <div style="padding:10px;text-align:center;"><b>{film['titre']}</b><br><span style="color:#D7001D">{film['score_sim']:.0f}% Match</span></div></div>'''
                st.markdown(card, unsafe_allow_html=True)
                if st.button("DÉTAILS", key=f"btn_{film['tconst']}_{i}", use_container_width=True):
                    st.session_state['detail_tconst'] = film['tconst']
                    st.rerun()
        
        if not st.session_state.get('show_all_recos') and len(filtered) > 5:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("VOIR PLUS"):
                st.session_state['show_all_recos'] = True
                st.rerun()

else:
    # --- MODE DÉTAILS ---
    m = df_movie[df_movie['tconst'] == detail_id].iloc[0]
    
    # Récupération Casting
    ids_p = df_link[df_link['tconst'] == detail_id]['nconst'].tolist()
    peoples = df_people[df_people['nconst'].isin(ids_p)]
    reals = peoples[peoples['person_professions'].str.contains('director', na=False)]['person_name'].tolist()
    acts = peoples[peoples['person_professions'].str.contains('actor|actress', na=False)]['person_name'].head(5).tolist()

    # Affichage
    c1, c2 = st.columns([1, 2])
    with c1:
        st.image(get_poster_url(m), use_container_width=True)
        
        # Bloc stats
        pop = m.get("movie_popularity", 0)
        vote = m.get("movie_vote_average_tmdb", 0)
        if pop or vote:
            st.markdown(f"""
            <div style="margin-top:20px;background:rgba(255,255,255,0.05);padding:15px;border-radius:15px;border:1px solid rgba(255,255,255,0.1);">
                <p style="color:#888;font-size:0.7rem;text-transform:uppercase;margin:0;">Popularité / Note</p>
                <p style="color:white;font-weight:800;font-size:1.1rem;margin:0;">{pop} | {vote}/10</p>
            </div>""", unsafe_allow_html=True)

    with c2:
        st.title(m['display_title'])
        st.subheader(f"{int(m['movie_startYear'])} • {int(m['movie_runtimeMinutes'])} min")
        st.markdown(f"**Genres:** {m['movie_genres_y']}")
        st.markdown(f"> {m['movie_overview_fr'] or m['movie_overview']}")
        st.markdown(f"**Réalisation:** {', '.join(reals)}")
        st.markdown(f"**Casting:** {', '.join(acts)}")
        
        # --- INTEGRATION LECTEUR VIDEO ---
        tr_url = m.get('trailer_url_fr') if pd.notna(m.get('trailer_url_fr')) else m.get('youtube_url', "")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if pd.notna(tr_url) and "http" in str(tr_url):
            st.markdown("#### 🎥 Bande-annonce")
            st.video(tr_url)
        else:
            st.info("Bande-annonce non disponible.")

        # Bouton Retour
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("RETOUR A LA LISTE", use_container_width=True):
            st.session_state['detail_tconst'] = None
            st.rerun()