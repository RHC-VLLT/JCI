import ast
import pandas as pd
import numpy as np
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

# ==================== 1. CONFIGURATION & STYLE ====================
st.set_page_config(
    page_title="Recommandation de films", 
    page_icon="🎬", 
    layout="wide"
)

# Style CSS pour une meilleure présentation
st.markdown("""
<style>
    /* Styles généraux */
    .similarity-badge {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 10px 18px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.2em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        text-align: center;
        display: block;
        margin-top: 15px; /* Pour centrer verticalement */
    }
    .genre-tag {
        background: #FF9800;
        color: white;
        padding: 4px 12px;
        border-radius: 12px;
        margin: 2px;
        display: inline-block;
        font-size: 0.85em;
    }
    .person-badge {
        background: #2196F3;
        color: white;
        padding: 5px 12px;
        border-radius: 15px;
        margin: 3px;
        display: inline-block;
        font-size: 0.9em;
    }
    .match-score {
        background: #9C27B0;
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        margin-left: 10px;
    }
    /* Correction de la taille du titre dans le container */
    [data-testid="stContainer"] h3 {
        margin-top: 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 2. FONCTIONS UTILITAIRES ====================

def extract_keywords(raw):
    """Transforme la chaîne JSON de TMDB en mots-clés lisibles."""
    if pd.isna(raw) or raw == "":
        return ""
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, list):
            # Remplacement des espaces pour créer des mots-clés uniques (ex: "QuentinTarantino")
            names = [d.get("name", "").replace(" ", "") for d in data if isinstance(d, dict)]
            return " ".join(names)
        return str(raw)
    except Exception:
        return str(raw)

def build_text_features(row):
    """Construit les features textuelles séparées pour le modèle hybride."""
    
    kw = extract_keywords(row.get("keywords", ""))
    keywords = kw if kw.strip() else ""
    
    overview = ""
    if str(row.get("movie_overview_fr", "")).strip():
        overview = str(row["movie_overview_fr"])
    elif str(row.get("movie_overview", "")).strip():
        overview = str(row["movie_overview"])
    
    tagline = str(row.get("movie_tagline_fr", "")).strip()
    if not tagline:
        tagline = str(row.get("movie_tagline", "")).strip()

    genres = str(row.get("movie_genres_y", "")).strip()
    
    return keywords, overview, genres, tagline

def simple_substring_search_movies(query, df_movie, limit=15):
    """Recherche simple de sous-chaîne (case-insensitive) pour trouver le film source."""
    if not query or len(query) < 2:
        return pd.DataFrame()
    
    query_lower = query.lower()
    
    mask = df_movie["movie_original_title"].str.lower().str.contains(query_lower, na=False)
    
    result = df_movie[mask].copy()
    
    result = result.sort_values("movie_popularity", ascending=False).head(limit)
    
    result["match_score"] = 100 
    
    return result

def get_people_for_movie(tconst, df_link, df_people, top_n=5):
    """Récupère les intervenants d'un film (acteurs, réalisateurs, etc.)."""
    try:
        movie_links = df_link[df_link["tconst"] == tconst]
        if movie_links.empty:
            return []
        
        people_info = movie_links.merge(df_people, on="nconst", how="left")
        people_info = people_info.drop_duplicates(subset=["person_name"])
        people_info = people_info[people_info["person_name"].notna()]
        
        people_list = []
        for _, row in people_info.head(top_n).iterrows():
            profession = str(row.get("person_professions", "")).replace(",", ", ")
            people_list.append({
                "name": row["person_name"],
                "profession": profession if profession and profession != "nan" else "Intervenant"
            })
        
        return people_list
    except Exception:
        return []

# ==================== 3. CHARGEMENT ET CONSTRUCTION DU MODÈLE ====================

@st.cache_data
def load_data():
    """Charge et prépare les données brutes, y compris l'URL du poster."""
    try:
        df_movie = pd.read_csv("movie.csv")
        
        text_cols = ["keywords", "movie_overview_fr", "movie_overview",
                     "movie_tagline_fr", "movie_genres_y", "movie_original_title",
                     "movie_poster_url_fr"] # <-- Ajout de la colonne d'URL
        for col in text_cols:
            if col in df_movie.columns:
                df_movie[col] = df_movie[col].fillna("")
        
        numeric_cols = ["movie_vote_average_tmdb", "movie_popularity", 
                        "movie_startYear", "movie_runtimeMinutes"]
        for col in numeric_cols:
            if col in df_movie.columns:
                df_movie[col] = pd.to_numeric(df_movie[col], errors='coerce').fillna(0)
        
        df_movie[["keywords_text", "overview_text", "genres_text", "tagline_text"]] = \
            df_movie.apply(build_text_features, axis=1, result_type='expand')
        
        df_people = pd.read_csv("intervenants.csv").rename(columns={
            "intervenant_primaryName": "person_name",
            "intervenant_primaryProfession": "person_professions",
            "intervenant_birthYear": "person_birthYear",
            "intervenant_deathYear": "person_deathYear",
        })
        df_link = pd.read_csv("intermediaire.csv")
        
        return df_movie, df_people, df_link
    
    except FileNotFoundError as e:
        st.error(f"❌ Fichier de données non trouvé : **{e.filename}**. Assurez-vous d'avoir les fichiers 'movie.csv', 'intervenants.csv', et 'intermediaire.csv' au bon endroit.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        st.stop()

@st.cache_resource
def build_advanced_recommender(df_movie):
    """Construit les matrices de features et les scalers pour le système hybride."""
    try:
        # 1. TF-IDF sur keywords
        tfidf_keywords = TfidfVectorizer(max_features=500, ngram_range=(1, 2), stop_words='english')
        keywords_matrix = tfidf_keywords.fit_transform(df_movie["keywords_text"])
        
        # 2. TF-IDF sur overview
        tfidf_overview = TfidfVectorizer(max_features=300, stop_words='english')
        overview_matrix = tfidf_overview.fit_transform(df_movie["overview_text"])
        
        # 3. TF-IDF sur genres
        tfidf_genres = TfidfVectorizer(max_features=50)
        genres_matrix = tfidf_genres.fit_transform(df_movie["genres_text"])
        
        # 4. Features numériques
        numeric_features = df_movie[["movie_vote_average_tmdb", "movie_popularity", 
                                      "movie_startYear", "movie_runtimeMinutes"]].values
        
        scaler = MinMaxScaler()
        numeric_normalized = scaler.fit_transform(numeric_features)
        
        return {
            "keywords_matrix": keywords_matrix,
            "overview_matrix": overview_matrix,
            "genres_matrix": genres_matrix,
            "numeric_features": numeric_normalized,
            "tfidf_keywords": tfidf_keywords,
            "tfidf_overview": tfidf_overview,
            "tfidf_genres": tfidf_genres,
            "scaler": scaler
        }
    except Exception as e:
        st.error(f"❌ Erreur lors de la construction du modèle de recommandation: {e}")
        st.stop()

def recommend_movies_hybrid(movie_title, df_movie, recommender_data, 
                           weight_keywords, weight_overview,
                           weight_genres, weight_numeric,
                           n_recommendations=5):
    """Calcule et renvoie les recommandations hybrides."""
    
    matches = df_movie[df_movie["movie_original_title"].str.lower() == movie_title.lower()]
    if matches.empty:
        return None, f"Film non trouvé : '{movie_title}'"
    
    movie_idx = matches.index[0]
    
    # Calcul des similarités
    sim_keywords = cosine_similarity(
        recommender_data["keywords_matrix"][movie_idx],
        recommender_data["keywords_matrix"]
    )[0]
    
    sim_overview = cosine_similarity(
        recommender_data["overview_matrix"][movie_idx],
        recommender_data["overview_matrix"]
    )[0]
    
    sim_genres = cosine_similarity(
        recommender_data["genres_matrix"][movie_idx],
        recommender_data["genres_matrix"]
    )[0]
    
    sim_numeric = cosine_similarity(
        [recommender_data["numeric_features"][movie_idx]],
        recommender_data["numeric_features"]
    )[0]
    
    # Score hybride pondéré
    hybrid_score = (
        weight_keywords * sim_keywords +
        weight_overview * sim_overview +  
        weight_genres * sim_genres +
        weight_numeric * sim_numeric     
    )
    
    # Récupérer les top N
    similar_indices = np.argsort(hybrid_score)[::-1]
    similar_indices_final = []
    for idx in similar_indices:
        if idx != movie_idx:
            similar_indices_final.append(idx)
        if len(similar_indices_final) >= n_recommendations:
            break
    
    # Construire le résultat
    recommendations = []
    for idx in similar_indices_final:
        movie_data = df_movie.iloc[idx]
        
        recommendations.append({
            "title": movie_data["movie_original_title"],
            "tconst": movie_data["tconst"],
            "similarity": hybrid_score[idx] * 100,
            "sim_keywords": sim_keywords[idx] * 100,
            "sim_overview": sim_overview[idx] * 100,
            "sim_genres": sim_genres[idx] * 100,
            "sim_numeric": sim_numeric[idx] * 100,
            "genres": movie_data.get("movie_genres_y", "N/A"),
            "overview": movie_data.get("movie_overview_fr", movie_data.get("movie_overview", "")),
            "tagline": movie_data.get("movie_tagline_fr", movie_data.get("movie_tagline", "")),
            "poster": movie_data.get("movie_poster_url_fr", ""), # <-- Récupération de l'URL du poster
            "year": movie_data.get("movie_startYear", "N/A"),
            "rating": movie_data.get("movie_vote_average_tmdb", "N/A"),
            "runtime": movie_data.get("movie_runtimeMinutes", "N/A")
        })
    
    return recommendations, None

# ==================== 4. INTERFACE PRINCIPALE (Streamlit) ====================

st.title("🎬 Système de Recommandation Intelligent")
st.markdown("Recommandations avancées basées sur **Contenu Pur** : **Style** (Keywords/Réalisateur) et **Genre**.")
st.markdown("---")

# Chargement
with st.spinner("🔄 Chargement et préparation du modèle..."):
    df_movie, df_people, df_link = load_data()
    recommender_data = build_advanced_recommender(df_movie)

st.success(f"✅ **{len(df_movie)}** films chargés | **{len(df_people)}** intervenants | Modèle basé sur le contenu prêt!")

# Sidebar avec contrôles avancés
with st.sidebar:
    st.header("⚙️ Paramètres de recommandation")
    
    st.subheader("🎚️ Pondération des critères")
    st.caption("Ajustement 50/50 pour la sélectivité du style vs genre (poids par défaut).")
    
    # --- PONDÉRATION : ÉQUILIBRE 50/50 ---
    weight_keywords_raw = st.slider("🔑 Keywords (Style/Réalisateur)", 0.0, 1.0, 0.50, 0.05,
                                help="Importance du style, du réalisateur et des mots-clés.")
    weight_genres_raw = st.slider("🎭 Genres (Catégorie)", 0.0, 1.0, 0.50, 0.05,
                              help="Importance des catégories de films (Crime, Thriller...).")
    # Valeurs forcées à 0.0 pour l'exclusion (visuel)
    weight_overview_raw = st.slider("📝 Synopsis (Contenu Narratif)", 0.0, 1.0, 0.00, 0.05, disabled=True,
                                help="Ce facteur est exclu de la recommandation (poids = 0).")
    weight_numeric_raw = st.slider("📊 Caractéristiques (Note/Pop./Année)", 0.0, 1.0, 0.00, 0.05, disabled=True,
                               help="Ce facteur est exclu de la recommandation (poids = 0).")
    # ------------------------------------------------------------------------
    
    # Normalisation pour que le total fasse 1.0
    total_weight = weight_keywords_raw + weight_genres_raw
    
    if total_weight > 0:
        weight_keywords = weight_keywords_raw / total_weight
        weight_overview = 0.0
        weight_genres = weight_genres_raw / total_weight
        weight_numeric = 0.0
    else:
        # Fallback si le total est zéro
        weight_keywords, weight_overview, weight_genres, weight_numeric = 0.5, 0.0, 0.5, 0.0
        total_weight = 1.0
    
    st.markdown("---")
    st.metric("Total Pondération Normalisée", f"1.00")
    
    st.markdown("---")
    st.subheader("📊 Statistiques des données")
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Films", f"{len(df_movie):,}")
    with col_b:
        st.metric("Personnes", f"{len(df_people):,}")

# Zone de recherche
col1, col2 = st.columns([5, 1])

with col1:
    search_query = st.text_input(
        "🔍 Recherche simple de titre",
        placeholder="Ex: Pulp Fiction, Fight Club...",
        help="Tapez une partie du titre pour trouver le film source."
    )

with col2:
    n_recos = st.selectbox("Nombre de recos", [3, 5, 7, 10], index=1, help="Nombre de films recommandés à afficher")

# Traitement de la recherche simple
if search_query and len(search_query) >= 2:
    with st.spinner("🔍 Recherche de titre en cours..."):
        matches = simple_substring_search_movies(search_query, df_movie, limit=15)
    
    if not matches.empty:
        st.subheader(f"📋 {len(matches)} résultat(s) trouvé(s) pour **'{search_query}'**")
        
        movie_options = {}
        for _, row in matches.iterrows():
            genres = row.get("movie_genres_y", "")
            
            display_name = f"{row['movie_original_title']}"
            if genres:
                display_name += f" - {genres}"
            
            movie_options[display_name] = row['movie_original_title']
        
        selected_display = st.selectbox("Sélectionnez le film source", list(movie_options.keys()))
        selected_movie = movie_options.get(selected_display)
        
        # Bouton de recommandation
        if selected_movie and st.button("🎯 Générer les recommandations", type="primary", use_container_width=True):
            with st.spinner(f"🤖 Analyse basée sur le contenu pour **{selected_movie}**..."):
                recommendations, error = recommend_movies_hybrid(
                    selected_movie, df_movie, recommender_data,
                    weight_keywords, weight_overview, weight_genres, weight_numeric,
                    n_recos
                )
                
                if error:
                    st.error(f"❌ {error}")
                elif recommendations:
                    st.markdown("---")
                    st.subheader(f"✨ Top {len(recommendations)} Recommandation(s) pour **{selected_movie}**")
                    
                    # Afficher les recommandations
                    for i, rec in enumerate(recommendations, 1):
                        with st.container(border=True):
                            # Colonnes pour l'affiche, les infos et le score
                            col_img, col_info, col_score = st.columns([1.5, 5, 1.5])
                            
                            # --- 1. AFFICHE ---
                            with col_img:
                                if rec['poster']:
                                    st.image(rec['poster'], width=180, caption=f"Film n°{i}")
                                else:
                                    st.warning("Affiche N/A")

                            # --- 2. INFORMATIONS DÉTAILLÉES ---
                            with col_info:
                                # Titre
                                title_display = f"**{i}. {rec['title']}**"
                                st.markdown(f"### {title_display}")
                                
                                # Genres
                                if rec['genres'] and str(rec['genres']) != 'nan':
                                    genres_list = rec['genres'].split(',')
                                    genres_html = " ".join([f'<span class="genre-tag">{g.strip()}</span>' for g in genres_list])
                                    st.markdown(genres_html, unsafe_allow_html=True)
                                
                                # Tagline
                                if rec['tagline'] and str(rec['tagline']) != 'nan':
                                    st.markdown(f"*{rec['tagline']}*")
                                
                                # Intervenants (à gauche, sous le texte)
                                people = get_people_for_movie(rec['tconst'], df_link, df_people, 5)
                                if people:
                                    st.markdown("---")
                                    st.markdown("**👥 Équipe Principale:**")
                                    people_html = ""
                                    for person in people:
                                        people_html += f'<span class="person-badge">{person["name"]}</span> '
                                    st.markdown(people_html, unsafe_allow_html=True)

                                # Synopsis et Détails (dans un expander)
                                with st.expander("🔍 Voir Synopsis et Score Détaillé"):
                                    # Synopsis
                                    if rec['overview'] and str(rec['overview']) != 'nan':
                                        st.markdown("**📖 Synopsis :**")
                                        overview_text = rec['overview']
                                        if len(overview_text) > 300:
                                            overview_text = overview_text[:300].rsplit(' ', 1)[0] + "..."
                                        st.write(overview_text)
                                    
                                    st.markdown("---")
                                    st.markdown("**📊 Répartition du Score (Sim. Cosinus) :**")
                                    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                                    col_s1.metric("Keywords", f"{rec['sim_keywords']:.0f}%")
                                    col_s2.metric("Synopsis", f"0%") 
                                    col_s3.metric("Genres", f"{rec['sim_genres']:.0f}%")
                                    col_s4.metric("Caract.", f"0%") 
                            
                            # --- 3. SCORE GLOBAL ---
                            with col_score:
                                st.markdown(f'<div class="similarity-badge">{rec["similarity"]:.0f}%</div>', 
                                    unsafe_allow_html=True)
                                st.caption("Score global contenu")
                                
    else:
        st.warning(f"⚠️ Aucun résultat de recherche trouvé pour '{search_query}'.")

else:
    st.info("👆 **Recherche de titre :** tapez **2-3 lettres** pour des suggestions.")

st.markdown("---")
st.caption("🤖 IA basée sur le contenu: TF-IDF (Keywords, Genres) + Sim. Cosinus Pondérée | © 2025")