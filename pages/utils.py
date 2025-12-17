import ast
import pandas as pd

def extract_keywords(raw):
    """Extrait les noms des mots-clés d'une structure liste/dict en chaîne de caractères."""
    if pd.isna(raw) or raw == "":
        return ""
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, list):
            return " ".join([d.get("name", "").replace(" ", "") for d in data if isinstance(d, dict)])
        return str(raw)
    except:
        return str(raw)

def build_text_features(row):
    """Prépare le texte pour le TF-IDF."""
    kw = extract_keywords(row.get("keywords", ""))
    keywords = kw if kw.strip() else ""
    overview = str(row.get("movie_overview_fr", row.get("movie_overview", "")))
    genres = str(row.get("movie_genres_y", "")).strip()
    return keywords, overview, genres

def get_poster_url(row):
    """Récupère la meilleure URL disponible pour le poster."""
    if pd.notna(row.get("movie_poster_url_fr")) and row.get("movie_poster_url_fr"):
        return str(row["movie_poster_url_fr"])
    elif pd.notna(row.get("movie_poster_path_fr")) and row.get("movie_poster_path_fr"):
        return f"https://image.tmdb.org/t/p/w500{row['movie_poster_path_fr']}"
    elif pd.notna(row.get("movie_poster_path_1")) and row.get("movie_poster_path_1"):
        return f"https://image.tmdb.org/t/p/w500{row['movie_poster_path_1']}"
    return ""