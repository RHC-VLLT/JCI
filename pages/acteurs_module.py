import streamlit as st
import pandas as pd

def translate_profession(prof):
    if not isinstance(prof, str): return ""
    trad = {
        "actor": "Acteur", "actress": "Actrice", "director": "Réalisateur",
        "writer": "Scénariste", "producer": "Producteur", "composer": "Compositeur"
    }
    parts = [p.strip().lower() for p in prof.split(",")]
    return ", ".join([trad.get(p, p.capitalize()) for p in parts])

def show_acteurs():
    # Récupération des données depuis le session_state (chargées dans app.py)
    df_actors = st.session_state.get('df_people')
    df_links = st.session_state.get('df_link')
    df_movies = st.session_state.get('df_movie')

    st.markdown("<h1 style='text-align:center; margin-bottom:30px;'>🎭 TALENTS DU CINÉMA</h1>", unsafe_allow_html=True)

    # --- BARRE DE RECHERCHE ---
    all_names = sorted(df_actors['person_name'].dropna().unique().tolist())
    
    c1, c2 = st.columns([4, 1])
    with c1:
        search_name = st.selectbox(
            "Rechercher un talent",
            options=[""] + all_names,
            format_func=lambda x: "🔎 Chercher un acteur, réalisateur..." if x == "" else x,
            label_visibility="collapsed"
        )
    with c2:
        if st.button("RECHERCHER", use_container_width=True) and search_name:
            found = df_actors[df_actors['person_name'] == search_name]
            if not found.empty:
                st.session_state.detail_actor_id = found.iloc[0]['nconst']
                st.rerun()

    st.markdown("---")

    # --- LOGIQUE D'AFFICHAGE ---
    detail_actor_id = st.session_state.get('detail_actor_id')

    if detail_actor_id:
        # >>> VUE DÉTAIL DE L'ACTEUR <<<
        actor = df_actors[df_actors['nconst'] == detail_actor_id].iloc[0]
        
        if st.button("⬅ RETOUR AUX TENDANCES"):
            st.session_state.detail_actor_id = None
            st.rerun()

        col_img, col_info = st.columns([1, 2.5], gap="large")
        
        with col_img:
            # Photo
            img_path = actor.get('tmdb_profile_url')
            if pd.isna(img_path) or str(img_path) == "nan":
                img_path = "https://via.placeholder.com/500x750?text=Image+Non+Disponible"
            st.image(img_path, use_container_width=True)
            st.markdown(f"<h2 style='text-align:center;'>{actor['person_name']}</h2>", unsafe_allow_html=True)

        with col_info:
            st.markdown('<div class="detail-container" style="padding:20px; background:rgba(255,255,255,0.05); border-radius:15px;">', unsafe_allow_html=True)
            prof_str = translate_profession(actor.get('person_professions'))
            birth = int(actor['person_birthYear']) if pd.notna(actor.get('person_birthYear')) and actor.get('person_birthYear') != 0 else "?"
            
            st.markdown(f"**Métier :** {prof_str}")
            st.markdown(f"**Année de naissance :** {birth}")
            st.markdown("### Biographie")
            bio = actor.get('tmdb_biography_fr')
            st.write(bio if pd.notna(bio) and str(bio).lower() != 'nan' else "Biographie non disponible.")
            st.markdown('</div>', unsafe_allow_html=True)

        # Section Filmographie
        st.markdown("### 🎞️ Filmographie")
        actor_tconsts = df_links[df_links['nconst'] == actor['nconst']]['tconst'].tolist()
        
        if actor_tconsts:
            my_movies = df_movies[df_movies['tconst'].isin(actor_tconsts)]
            if not my_movies.empty:
                cols = st.columns(5)
                for i, (_, film) in enumerate(my_movies.iterrows()):
                    with cols[i % 5]:
                        poster = film.get('movie_poster_url_fr') or "https://via.placeholder.com/300x450?text=No+Poster"
                        st.image(poster, use_container_width=True)
                        st.caption(f"**{film.get('display_title')}**")
        else:
            st.info("Aucun film trouvé pour cet artiste.")

    else:
        # >>> VUE GRILLE TENDANCE <<<
        st.subheader("🔥 En vedette")
        # On prend les acteurs qui ont une photo en priorité
        top_actors = df_actors.dropna(subset=['tmdb_profile_url']).head(12)
        
        cols = st.columns(6)
        for idx, (_, row) in enumerate(top_actors.iterrows()):
            with cols[idx % 6]:
                st.image(row['tmdb_profile_url'], use_container_width=True)
                st.markdown(f"<p style='text-align:center; font-weight:bold;'>{row['person_name']}</p>", unsafe_allow_html=True)
                if st.button("VOIR PROFIL", key=f"grid_{row['nconst']}", use_container_width=True):
                    st.session_state.detail_actor_id = row['nconst']
                    st.rerun()