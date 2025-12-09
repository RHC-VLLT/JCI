import streamlit as st


# 1. Configuration de la page (Mode large)
st.set_page_config(layout="wide", page_title="Just Creuse It")


# 2. Le Design (CSS simplifié)
# On met le fond en NOIR et on centre la barre de menu
st.markdown("""
<style>
       /* Fond de la page en NOIR */
        .stApp {
        background-color: black;
    }
       /* Tout le texte en BLANC */
        h1, h2, h3, p, div {
        color: white;
    }


       /* La Barre de Navigation (Centrée) */
        .navbar {
            padding: 20px;
           text-align: center; /* Pour centrer les liens */
            background-color: black;
            border-bottom: 1px solid #333; /* Petite ligne grise en dessous */
            margin-bottom: 30px;
    }
        .navbar a {
            color: white;
            text-decoration: none;
           margin: 0 20px; /* Espace entre les mots */
            font-size: 18px;
            font-weight: bold;
            text-transform: uppercase;
    }
        .navbar a:hover {
           color: #D7001D; /* Rouge au survol */
    }
</style>
""", unsafe_allow_html=True)


# 3. Affichage de la Barre de Navigation
st.markdown("""
    <div class="navbar">
        <a href="#"> Accueil</a>
        <a href="#"> Films</a>
        <a href="#"> Séries</a>
        <a href="#"> Recherche</a>
</div>
""", unsafe_allow_html=True)




# --- PAGE 1 : L'IMAGE POPCORN & LE TEXTE ---


# On crée 2 colonnes : Image à gauche, Texte à droite
col1, col2 = st.columns([1, 1], gap="medium")


with col1:
# Ton image locale (Assure-toi qu'elle s'appelle bien popcorn.jpg)
    try:
        st.image("popcorn.jpg", use_container_width=True)
    except:
        st.warning("⚠️ Image 'popcorn.jpg' introuvable.")


with col2:
    st.markdown("<br><br>", unsafe_allow_html=True) # Espaces pour descendre le texte
    st.title("LE CINÉMA QUI FAIT BATTRE LE CŒUR CREUSOIS")
    st.write("Découvrez les meilleures pépites locales.")
    st.button("VOIR LE FILM >>>")




# --- SÉPARATION ---
st.markdown("<hr style='border: 1px solid #333; margin: 50px 0;'>", unsafe_allow_html=True)




# --- PAGE 2 : LA VIDÉO SCOOBY ---


st.markdown("<h2 style='text-align: center;'>VOTRE RECOMMANDATION</h2>", unsafe_allow_html=True)


# On centre la vidéo avec des colonnes [Vide, Vidéo, Vide]
c_left, c_center, c_right = st.columns([1, 3, 1])


with c_center:
    try:
        # Ta vidéo locale
        st.video("scooby.mp4")
    except:
        st.warning("⚠️ Vidéo 'scooby.mp4' introuvable.")




# --- SÉPARATION ---
st.markdown("<hr style='border: 1px solid #333; margin: 50px 0;'>", unsafe_allow_html=True)




# --- PAGE 3 : LA RECHERCHE ---


# On centre la recherche
c_search_L, c_search_M, c_search_R = st.columns([1, 2, 1])


with c_search_M:
    st.markdown("<h2 style='text-align: center;'>TROUVEZ VOTRE FILM</h2>", unsafe_allow_html=True)

# Barre de saisie
    search = st.text_input("Recherche", placeholder="Titre, Genre...", label_visibility="collapsed")
# Bouton qui prend toute la largeur
    if st.button("SURPRENEZ-MOI !", use_container_width=True):
        st.success(f"Recherche : {search}")


st.markdown("<br><br>", unsafe_allow_html=True)

