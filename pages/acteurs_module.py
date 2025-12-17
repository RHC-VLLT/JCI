import streamlit as st
import pandas as pd

def translate_profession(prof):
    """Traduit les métiers en français proprement."""
    if not isinstance(prof, str): return ""
    trad = {
        "actor": "Acteur", "actress": "Actrice", "director": "Réalisateur",
        "writer": "Scénariste", "producer": "Producteur", "composer": "Compositeur"
    }
    parts = [p.strip().lower() for p in prof.split(",")]
    return ", ".join([trad.get(p, p.capitalize()) for p in parts])

def show_acteurs():
    """Affiche la page des talents avec recherche instantanée corrigée."""
    df_actors = st.session_state.get('df_people')
    df_links = st.session_state.get('df_link')
    df_movies = st.session_state.get('df_movie')

    st.markdown("<h1 style='text-align:center; margin-bottom:30px;'>🎭 TALENTS DU CINÉMA</h1>", unsafe_allow_html=True)

    # --- BARRE DE RECHERCHE CORRIGÉE ---
    all_names = sorted(df_actors['person_name'].dropna().unique().tolist())
    
    # On définit une fonction de rappel (callback) pour forcer la mise à jour
    def on_actor_change():
        selected = st.session_state.actor_search_key
        if selected:
            found = df_actors[df_actors['person_name'] == selected]
            if not found.empty:
                st.session_state.detail_actor_id = found.iloc[0]['nconst']

    search_name = st.selectbox(
        "Rechercher un talent",
        options=[""] + all_names,
        index=0,
        format_func=lambda x: "🔎 Chercher un acteur, réalisateur..." if x == "" else x,
        label_visibility="collapsed",
        key="actor_search_key",
        on_change=on_actor_change
    )

    st.markdown("---")

    detail_actor_id = st.session_state.get('detail_actor_id')

    if detail_actor_id:
        # >>> VUE DÉTAIL DE L'ACTEUR <<<
        actor = df_actors[df_actors['nconst'] == detail_actor_id].iloc[0]
        
        if st.button("⬅ RETOUR AUX TENDANCES"):
            st.session_state.detail_actor_id = None
            st.rerun()

        col_img, col_info = st.columns([1, 2.5], gap="large")
        
        with col_img:
            img_path = actor.get('tmdb_profile_url')
            if pd.isna(img_path) or str(img_path) == "nan":
                img_path = "https://via.placeholder.com/500x750?text=Pas+d'image"
            st.image(img_path, use_container_width=True)
            st.markdown(f"<h2 style='text-align:center;'>{actor['person_name']}</h2>", unsafe_allow_html=True)

        with col_info:
            # Métier
            prof_str = translate_profession(actor.get('person_professions'))
            st.markdown(f"**Métier :** {prof_str}")
            
            # Année de naissance (Caché si absent)
            birth = actor.get('person_birthYear')
            if pd.notna(birth) and birth != 0:
                st.markdown(f"**Année de naissance :** {int(birth)}")
            
            # Biographie (Caché si absent)
            bio = actor.get('tmdb_biography_fr')
            if pd.notna(bio) and str(bio).lower() not in ['nan', 'biographie non disponible.']:
                st.markdown("### Biographie")
                st.write(bio)

            # FILMOGRAPHIE (À côté de la photo)
            st.markdown("### 🎞️ Filmographie")
            actor_tconsts = df_links[df_links['nconst'] == actor['nconst']]['tconst'].tolist()
            
            if actor_tconsts:
                my_movies = df_movies[df_movies['tconst'].isin(actor_tconsts)]
                if not my_movies.empty:
                    cols_film = st.columns(4)
                    for i, (_, film) in enumerate(my_movies.head(12).iterrows()):
                        with cols_film[i % 4]:
                            poster = film.get('movie_poster_url_fr') or "https://via.placeholder.com/300x450?text=No+Poster"
                            st.image(poster, use_container_width=True)
                            st.caption(f"**{film.get('display_title')}**")
    else:
        # >>> VUE GRILLE TENDANCE <<<
        st.subheader("🔥 Les plus populaires")
        
        # Tri par popularité
        top_actors = df_actors.sort_values('tmdb_popularity', ascending=False).head(24)
        
        cols = st.columns(6)
        for idx, (_, row) in enumerate(top_actors.iterrows()):
            with cols[idx % 6]:
                img_p = row.get('tmdb_profile_url')
                img_p = img_p if pd.notna(img_p) and str(img_p) != "nan" else "https://via.placeholder.com/500x750?text=No+Image"
                
                st.image(img_p, use_container_width=True)
                st.markdown(f"<p style='text-align:center; font-weight:bold; font-size:0.9rem;'>{row['person_name']}</p>", unsafe_allow_html=True)
                if st.button("VOIR PROFIL", key=f"btn_act_{row['nconst']}", type="primary", use_container_width=True):
                    st.session_state.detail_actor_id = row['nconst']
                    st.rerun()