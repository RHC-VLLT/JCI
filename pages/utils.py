import ast
import pandas as pd

def extract_keywords(raw):
    if pd.isna(raw) or raw == "": return ""
    try:
        data = ast.literal_eval(raw)
        if isinstance(data, list):
            return " ".join([d.get("name", "").replace(" ", "") for d in data if isinstance(d, dict)])
        return str(raw)
    except: return str(raw)

def build_text_features(row):
    kw = extract_keywords(row.get("keywords", ""))
    ov = str(row.get("movie_overview_fr", row.get("movie_overview", "")))
    gn = str(row.get("movie_genres_y", "")).strip()
    return kw, ov, gn

def get_poster_url(row):
    if pd.notna(row.get("movie_poster_url_fr")) and row.get("movie_poster_url_fr"): return str(row["movie_poster_url_fr"])
    elif pd.notna(row.get("movie_poster_path_fr")) and row.get("movie_poster_path_fr"): return f"https://image.tmdb.org/t/p/w500{row['movie_poster_path_fr']}"
    return ""