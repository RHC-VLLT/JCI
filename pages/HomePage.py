import streamlit as st
import time
import os


# CONFIGURATION DE LA PAGE

# "layout=wide" permet d'utiliser toute la largeur de la page
st.set_page_config(page_title="Accueil", layout="wide")



# LIENS GOOGLE DRIVE (À REMPLACER PAR TES LIENS REELS)


logo_url = "assets/Logo_JCI_1.png"
background_url = "assets/Acceuil_Pic_1_Page_1.jpg"




# STYLE DE LA BARRE DE NAVIGATION (NAVBAR)

navbar_style = """
<style>
/* Le conteneur de la barre */
.navbar {
    display: flex;
    justify-content: flex-start;
    align-items: center;
    background-color: black;
    padding: 12px 30px;
}

/* Lien de navigation */
.navbar a {
    color: white;
    text-decoration: none;
    margin-right: 30px;
    font-size: 18px;
    font-weight: 500;
}

/* Logo image */
.navbar img {
    height: 40px;
    margin-right: 40px;
}
</style>
"""

# Ajout du CSS dans la page
st.markdown(navbar_style, unsafe_allow_html=True)


# HTML DE LA BARRE DE NAVIGATION

# NOTE :
# "/" = page d'accueil
# Les autres pages seront dans le dossier "pages"
st.markdown(
    f"""
<div class="navbar">
    <a href="/">
        <img src="{logo_url}" alt="logo">
    </a>
    <a href="/">Accueil</a>
    <a href="/Reco_Top_Films_at_Tim">Films</a>
    <a href="/Reco_Top_Actors_Films_at_Tim">Acteurs</a>
    <a href="/Reco_Top_Genrs_Films_at_Tim">Genres</a>
</div>
""",
    unsafe_allow_html=True,
)



# GESTION DE LA PAGE D'INTRODUCTION (DUREE 3 SECONDES)

# On utilise une variable enregistrée dans la session
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False

# Si l'intro n'a pas encore été jouée :
if not st.session_state.intro_done:


    # Image de fond (background)

    page_bg = f"""
    <style>
    .stApp {{
        background-image: url("{background_url}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
    }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)


    # Texte de slogan

    st.markdown(
        "<h2 style='color: white; font-weight: 700;'>Votre Film Parfait Commence Ici</h2>",
        unsafe_allow_html=True
    )

    # Bouton vers l'accueil
    bouton = st.button("Le Film Parfait à la Carte")

    if bouton:
        st.session_state.intro_done = True
        st.rerun()

    # Attendre 3 secondes puis passer à la page suivante
    time.sleep(3)
    st.session_state.intro_done = True
    st.rerun()


# PAGE D'ACCUEIL (après les 3 secondes)
else:
    st.title("Bienvenue sur l'accueil")
    st.write("Cette page s'affiche après l'écran d'introduction.")
