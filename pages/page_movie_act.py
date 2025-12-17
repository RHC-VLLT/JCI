import math
import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# ================== CONFIG ==================
st.set_page_config(page_title="Movies by Genre", layout="wide")

# ================== STYLE ==================
st.markdown(
    """
    <style>
    /* Carte */
    .movie-card {
        display: flex;
        flex-direction: column;
        align-items: center;
    }

    /* Affiches uniformes */
    .poster {
        width: 100%;
        height: 320px;
        object-fit: cover;
        border-radius: 10px;
        display: block;
        margin-bottom: 14px;
    }

    /* Bouton rouge */
    div.stButton > button {
        color: #e50914;
        border: 2px solid #e50914;
        background-color: transparent;
        border-radius: 20px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }

    div.stButton > button:hover {
        background-color: #e50914;
        color: white;
        border-color: #e50914;
    }
    
    /* ================= SELECTBOX ================= */
    div[data-baseweb="select"] > div {
        border: 2px solid #e50914 !important;
        border-radius: 20px !important;
        background-color: transparent !important;
        min-height: 44px;
    }

    div[data-baseweb="select"] span {
        color: #e50914 !important;
        font-weight: 600;
    }

    div[data-baseweb="select"] svg {
        fill: #e50914 !important;
    }

    div[data-baseweb="select"] > div:hover {
        background-color: rgba(229, 9, 20, 0.08) !important;
    }

    ul[role="listbox"] {
        border: 2px solid #e50914 !important;
        border-radius: 16px !important;
        background-color: #0e0e0e !important;
    }

    ul[role="listbox"] li:hover {
        background-color: #e50914 !important;
        color: white !important;
    }

    /* ===== LABELS (Streamlit 1.51+) ===== */
    div[data-testid="stWidgetLabel"] p,
    div[data-testid="stWidgetLabel"] span {
        font-size: 35px !important;
        font-weight: 800 !important;
        line-height: 1.2 !important;
    }
    
.actor-name {
    text-align: center;
    font-weight: 700;
    margin-top: 6px;
    font-size: 0.95rem;
    line-height: 1.2;
    min-height: 2.6em;   /* 👈 clé du problème */
    display: flex;
    align-items: center;
    justify-content: center;
}
    </style>
    """,
    unsafe_allow_html=True
)

# ================== DATA ==================
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df

df = load_data("movie.csv")

# ✅ AJOUT : données intervenants / acteurs
intermediaire = load_data("intermediaire.csv")   # attendu: tconst, nconst (+ éventuellement ordering)
intervenants  = load_data("intervenants.csv")    # attendu: nconst, intervenant_primaryName, intervenant_primaryProfession, tmdb_profile_url

def _clean_url(u):
    if u is None or (isinstance(u, float) and np.isnan(u)):
        return None
    u = str(u).strip()
    if not u or u.lower() == "nan":
        return None
    if u.startswith("http://"):
        u = "https://" + u[len("http://"):]
    return u if u.startswith("http") else None

def get_top_actors_for_movie(tconst: str, top_n: int = 10) -> pd.DataFrame:
    """Retourne jusqu'à top_n acteurs/actrices du film (nom + photo), sans popularité."""
    if not {"tconst", "nconst"}.issubset(set(intermediaire.columns)):
        return pd.DataFrame(columns=["name", "photo"])
    if "nconst" not in intervenants.columns:
        return pd.DataFrame(columns=["name", "photo"])

    links = intermediaire[intermediaire["tconst"] == tconst].copy()
    if links.empty:
        return pd.DataFrame(columns=["name", "photo"])

    # Si on a une colonne d'ordre (cast billing), on l'utilise
    order_col = None
    for c in ["ordering", "cast_order", "order", "billing_order", "position"]:
        if c in links.columns:
            order_col = c
            break

    m = links.merge(intervenants, on="nconst", how="left")

    name_col = "intervenant_primaryName" if "intervenant_primaryName" in m.columns else None
    prof_col = "intervenant_primaryProfession" if "intervenant_primaryProfession" in m.columns else None
    photo_col = "tmdb_profile_url" if "tmdb_profile_url" in m.columns else None

    # Filtre acteurs/actrices si possible (sinon on garde tout)
    if prof_col:
        m = m[m[prof_col].astype(str).str.contains(r"\bactor\b|\bactress\b", case=False, na=False)]

    # Tri selon l'ordre de casting si dispo
    if order_col and order_col in m.columns:
        m[order_col] = pd.to_numeric(m[order_col], errors="coerce")
        m = m.sort_values(order_col, ascending=True, na_position="last")

    # Priorise ceux qui ont une photo (sans éliminer si pas assez)
    if photo_col:
        m["_has_photo"] = m[photo_col].apply(lambda x: 1 if isinstance(_clean_url(x), str) else 0)
        m = m.sort_values("_has_photo", ascending=False)

    m = m.drop_duplicates(subset=["nconst"]).head(top_n)

    out = pd.DataFrame({
        "name": m[name_col] if name_col else m["nconst"],
        "photo": m[photo_col] if photo_col else None,
    }).reset_index(drop=True)

    out["photo"] = out["photo"].apply(_clean_url)
    return out

def render_actors_grid(actors_df: pd.DataFrame, per_row: int = 5):
    """Affiche les acteurs en grille (photo + nom), sans popularité."""
    if actors_df.empty:
        st.caption("Aucun acteur trouvé pour ce film.")
        return

    rows = math.ceil(len(actors_df) / per_row)
    idx = 0
    for _ in range(rows):
        cols = st.columns(per_row)
        for j in range(per_row):
            if idx >= len(actors_df):
                break
            a = actors_df.iloc[idx]
            idx += 1

            name = str(a.get("name", ""))
            photo = a.get("photo", None)

            with cols[j]:
                if isinstance(photo, str) and photo.startswith("http"):
                    st.image(photo, width=95)
                else:
                    st.write("🧑")
                st.markdown(f"**{name}**")


GENRE_COL = "movie_genres_y"
TITLE_COL = "title"
POSTER_COL = "movie_poster_url_fr"
TRAILER_COL = "trailer_url_fr"

OVERVIEW_COLS = ["movie_overview_fr", "movie_overview"]
TAGLINE_COLS = ["movie_tagline_fr", "movie_tagline"]

# ================== UI ==================
st.title("🎬 Choisissez votre séance")

# Genres
if GENRE_COL in df.columns:
    all_genres = (
        df[GENRE_COL]
        .dropna()
        .astype(str)
        .str.split(",")
        .explode()
        .str.strip()
        .replace("", np.nan)
        .dropna()
        .unique()
        .tolist()
    )
    all_genres = sorted(all_genres)
else:
    all_genres = []


st.subheader("🎞️ Qu'est ce qu'on regarde ce soir ? ")

st.markdown('<div id="genre_anchor"></div>', unsafe_allow_html=True)
    
# ─── Ligne 1 : Genre
chosen_genre = st.selectbox(
    "🍿 Genre",
    ["(Tous)"] + all_genres if all_genres else ["(Genre column not found)"],
    index=0,
    key="genre"
)

# ─── Ligne 2 : Films affichés par page (à gauche)
size_col, nav_col = st.columns([1, 1], gap="large")

with size_col:
    page_size = st.selectbox(
        "Films affichés par page",
        options=[5, 10, 20, 50],
        index=0,
        key="page_size"
    )

# ================== FILTER ==================
df_f = df.copy()

if chosen_genre != "(Tous)" and GENRE_COL in df_f.columns:
    df_f = df_f[df_f[GENRE_COL].astype(str).str.contains(chosen_genre, case=False, na=False)]

if "movie_popularity" in df_f.columns:
    df_f["movie_popularity"] = pd.to_numeric(df_f["movie_popularity"], errors="coerce")
    df_f = df_f.sort_values("movie_popularity", ascending=False, na_position="last")

total = len(df_f)
st.caption(f"{total} film(s) trouvés")

if total == 0:
    st.stop()

# ─── Maintenant seulement : Navigation (à droite)
total_pages = max(1, math.ceil(total / page_size))
page_labels = [f"Page {i} / {total_pages}" for i in range(1, total_pages + 1)]

with nav_col:
    page_label = st.selectbox(
        "Navigation",
        page_labels,
        index=0,
        key="navigation"
    )

# ================== STATE ==================
if "selected_tconst" not in st.session_state:
    st.session_state.selected_tconst = None

# ================== PAGINATION ==================
# ✅ on récupère la page choisie dans le selectbox du haut
page_label = st.session_state["navigation"]
page = int(page_label.split()[1])

start = (page - 1) * page_size
end = start + page_size
page_df = df_f.iloc[start:end].reset_index(drop=True)

st.write(f"Films **{start+1} à {min(end, total)}** — Page **{page}/{total_pages}**")

# ================== GRID ==================
cards_per_row = 5
rows = math.ceil(len(page_df) / cards_per_row)

for r in range(rows):
    cols = st.columns(cards_per_row)
    for c in range(cards_per_row):
        idx = r * cards_per_row + c
        if idx >= len(page_df):
            break

        row = page_df.iloc[idx]
        poster = row.get(POSTER_COL)
        tconst = row.get("tconst")

        with cols[c]:
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)

            if isinstance(poster, str) and poster.startswith("http"):
                st.markdown(
                    f'<img src="{poster}" class="poster" />',
                    unsafe_allow_html=True
                )
            else:
                st.write("🖼️ Pas d'affiche")

            # Bouton centré sous l'affiche
            c1, c2, c3 = st.columns([1, 2, 1])
            with c2:
                if st.button("Voir la fiche", key=f"open_{tconst}", use_container_width=True):
                    st.session_state.selected_tconst = tconst
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

# ================== SCROLL ==================
st.divider()
st.markdown('<div id="film_fiche"></div>', unsafe_allow_html=True)

if st.session_state.selected_tconst:
    components.html(
        """
        <script>
          const el = window.parent.document.getElementById("film_fiche");
          if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
        </script>
        """,
        height=0,
    )

# ================== FICHE FILM ==================
sel = st.session_state.selected_tconst
if sel:
    film = df[df["tconst"] == sel].iloc[0]

    st.subheader(f"📌 {film.get(TITLE_COL)}")

    left, right = st.columns([1, 2], gap="large")

    with left:
        if isinstance(film.get(POSTER_COL), str):
            st.image(film.get(POSTER_COL), use_container_width=True)

        if st.button("⬅️ Retour aux résultats"):
            st.session_state.selected_tconst = None
            st.session_state["_scroll_to"] = "genre_anchor"
            st.rerun()

    with right:
        for col in TAGLINE_COLS:
            if col in df.columns and pd.notna(film.get(col)):
                st.info(film.get(col))
                break

        for col in OVERVIEW_COLS:
            if col in df.columns and pd.notna(film.get(col)):
                st.markdown("### Synopsis")
                st.write(film.get(col))
                break

        trailer = film.get(TRAILER_COL)
        if isinstance(trailer, str) and trailer.startswith("http"):
            st.markdown("### Trailer")
            st.video(trailer)
        else:
            st.caption("Trailer non disponible.")

        # ✅ AJOUT : Acteurs (max 10) avec photo (tmdb_profile_url), sans popularité
        st.markdown("### 📌 Acteurs principaux")
        actors_df = get_top_actors_for_movie(sel, top_n=10)
        render_actors_grid(actors_df, per_row=5)
        
# ================== SCROLL FINAL (TOUT EN BAS) ==================
anchor = st.session_state.get("_scroll_to", None)

if anchor:
    components.html(
        f"""
        <script>
          const targetId = "{anchor}";
          const doc = window.parent.document;

          function getScrollRoot() {{
            return doc.querySelector('section.main')
              || doc.querySelector('div[data-testid="stAppViewContainer"]')
              || doc.documentElement;
          }}

          function forceScroll(attempt = 0) {{
            const el = doc.getElementById(targetId);
            const root = getScrollRoot();

            if (el) {{
              el.scrollIntoView({{ behavior: "smooth", block: "start" }});
            }} else {{
              root.scrollTo({{ top: 0, behavior: "smooth" }});
            }}

            if (attempt < 20) {{
              setTimeout(() => forceScroll(attempt + 1), 100);
            }}
          }}

          setTimeout(() => forceScroll(0), 50);
        </script>
        """,
        height=0,
    )
    st.session_state["_scroll_to"] = None

