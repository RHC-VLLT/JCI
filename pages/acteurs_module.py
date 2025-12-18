import streamlit as st
import pandas as pd

DEFAULT_USER_IMG = "https://cdn-icons-png.flaticon.com/512/149/149071.png"

def translate_profession(prof):
    if not isinstance(prof, str): return ""
    trad = {"actor": "Acteur", "actress": "Actrice", "director": "Réalisateur", "writer": "Scénariste", "producer": "Producteur"}
    return ", ".join([trad.get(p.strip().lower(), p.capitalize()) for p in prof.split(",")])

def show_acteurs():
    df_actors = st.session_state.get('df_people')
    df_links = st.session_state.get('df_link')
    df_movies = st.session_state.get('df_movie')

    st.markdown("<h1 style='text-align:center; margin-bottom:30px;'> TALENTS DU CINÉMA</h1>", unsafe_allow_html=True)

    all_names = sorted(df_actors['person_name'].dropna().unique().tolist())
    def on_actor_change():
        if st.session_state.actor_search_key:
            found = df_actors[df_actors['person_name'] == st.session_state.actor_search_key]
            if not found.empty: 
                # On utilise nconst de manière sécurisée
                st.session_state.detail_actor_id = found.iloc[0].get('nconst')

    st.selectbox("Chercher un talent", options=[""] + all_names, index=0, key="actor_search_key", on_change=on_actor_change, label_visibility="collapsed")

    detail_id = st.session_state.get('detail_actor_id')

    if detail_id:
        actor_rows = df_actors[df_actors['nconst'] == detail_id]
        if actor_rows.empty:
            st.error("Profil non trouvé.")
            if st.button("⬅ RETOUR"): st.session_state.detail_actor_id = None; st.rerun()
            return
            
        actor = actor_rows.iloc[0]
        if st.button("⬅ RETOUR"):
            st.session_state.detail_actor_id = None
            st.rerun()

        col_img, col_info = st.columns([1, 2.5], gap="large")
        with col_img:
            img = actor.get('tmdb_profile_url')
            img = img if pd.notna(img) and str(img).lower() not in ["nan", ""] else DEFAULT_USER_IMG
            st.image(img, use_container_width=True)
            st.markdown(f"<h2 style='text-align:center;'>{actor['person_name']}</h2>", unsafe_allow_html=True)

        with col_info:
            st.markdown(f"**Métier :** {translate_profession(actor.get('person_professions'))}")
            birth = actor.get('person_birthYear')
            if pd.notna(birth) and birth != 0:
                st.markdown(f"**Naissance :** {int(birth)}")
            
            bio = actor.get('tmdb_biography_fr')
            if pd.notna(bio) and str(bio).lower() not in ['nan', 'biographie non disponible.']:
                st.markdown("### Biographie")
                st.write(bio)

            st.markdown("### 🎞️ Filmographie")
            actor_films = df_links[df_links['nconst'] == detail_id]['tconst'].tolist()
            if actor_films:
                my_movies = df_movies[df_movies['tconst'].isin(actor_films)].head(12)
                cols_f = st.columns(4)
                for i, (_, f) in enumerate(my_movies.iterrows()):
                    with cols_f[i % 4]:
                        poster = f.get('movie_poster_url_fr') or "https://via.placeholder.com/300x450?text=Affiche+manquante"
                        st.markdown(f'''<div class="movie-card-container"><img src="{poster}" class="movie-poster-img"></div>''', unsafe_allow_html=True)
                        if st.button("DÉTAILS", key=f"act_f_{f['tconst']}", type="primary", use_container_width=True):
                            st.session_state.detail_tconst = f['tconst']
                            st.session_state.current_page = "FILMS"
                            st.rerun()
    else:
        top_actors = df_actors.sort_values('tmdb_popularity', ascending=False).head(24)
        cols = st.columns(6)
        for idx, (_, row) in enumerate(top_actors.iterrows()):
            with cols[idx % 6]:
                img = row.get('tmdb_profile_url')
                img = img if pd.notna(img) and str(img).lower() not in ["nan", ""] else DEFAULT_USER_IMG
                st.image(img, use_container_width=True)
                st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:0.8rem;'>{row['person_name']}</p>", unsafe_allow_html=True)
                if st.button("VOIR", key=f"grid_{row.get('nconst')}", type="primary", use_container_width=True):
                    st.session_state.detail_actor_id = row.get('nconst')
                    st.rerun()