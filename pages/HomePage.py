import streamlit as st
import time
import os
import base64

# --- CONFIGURATION DES CHEMINS D'ACCÈS (AJUSTER SI NÉCESSAIRE) ---
# Le code suppose que les assets sont dans un dossier 'assets' au même niveau que le dossier 'pages'
base_dir = os.path.join(os.path.dirname(__file__), "..", "assets")

# Assets utilisés dans le Code 2 (pour la barre de nav et le splash screen)
logo_path = os.path.join(base_dir, "Logo_JCI_1.png")
background_path = os.path.join(base_dir, "Acceuil_Pic_1_Page_1.jpg")



# --- FONCTION UTILITAIRE POUR ENCODER LES IMAGES ---
def image_to_base64(image_path):
    """Encode une image locale en Base64 pour l'utiliser directement dans le HTML/CSS."""
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        # Assurez-vous d'avoir le bon type MIME si ce n'est pas un png (ex: image/jpeg)
        extension = os.path.splitext(image_path)[1].lower().replace('.', '')
        mime_type = f"image/{'jpeg' if extension == 'jpg' else extension}"
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        st.error(f"⚠️ Fichier non trouvé : {image_path}. Veuillez vérifier le chemin.")
        return ""
    except Exception as e:
        st.error(f"⚠️ Erreur lors de l'encodage de l'image : {e}")
        return ""

# Conversion des assets en Base64
logo_url_base64 = image_to_base64(logo_path)
background_url_base64 = image_to_base64(background_path)


# --- CONFIGURATION DE LA PAGE GLOBALE ---
st.set_page_config(layout="wide", page_title="Just Creuse It")

# On utilise une variable enregistrée dans la session pour gérer l'intro
if "intro_done" not in st.session_state:
    st.session_state.intro_done = False


# --- GESTION DE LA PAGE D'INTRODUCTION (SPLASH SCREEN) ---
if not st.session_state.intro_done:

    # 1. Image de fond pour le Splash Screen
    # Le CSS va couvrir tout l'écran avec l'image encodée
    page_bg = f"""
    <style>
    /* Utilise l'image de fond encodée */
    [data-testid="stAppViewBlock"] {{
        background-image: url("{background_url_base64}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
    }}
    /* Le texte sera bien visible sur l'image */
    h2, h1, p {{ color: white; }}
    /* Cache l'élément de la barre de navigation pendant l'intro */
    .navbar {{ display: none; }}
    </style>
    """
    st.markdown(page_bg, unsafe_allow_html=True)

    # 2. Contenu Centré du Splash Screen
    # Ajout d'espaces pour centrer verticalement (approche simple)
    st.markdown("<br>" * 10, unsafe_allow_html=True)

    st.markdown(
        "<h2 style='text-align: center; font-weight: 700; font-size: 3em;'>Votre Film Parfait Commence Ici</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; font-size: 1.5em; margin-bottom: 50px;'>Just Creuse It</p>",
        unsafe_allow_html=True
    )

    # 3. Bouton Centré
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        # On utilise une clé pour s'assurer que l'état est géré correctement
        bouton = st.button("ACCÉDER AU CINÉMA", key="intro_button", use_container_width=True)

    # Logique pour passer à la page principale
    if bouton:
        st.session_state.intro_done = True
        st.rerun()

    # Attendre 3 secondes puis passer à la page suivante automatiquement
    time.sleep(3)
    st.session_state.intro_done = True
    st.rerun()


# --- PAGE PRINCIPALE (APRÈS LE SPLASH SCREEN) ---
else:

    # 1. Reset du fond d'écran et Styles pour la Page Principale
    st.markdown("""
    <style>
    /* Reset le background image et applique le fond noir */
    [data-testid="stAppViewBlock"] {
        background-image: none !important;
        background-color: black !important;
    }

    /* Tout le texte en BLANC (pour le contenu) */
    h1, h2, h3, p, div, label {
        color: white;
    }

    /* --- Style de la Barre de Navigation (NAVBAR) --- */
    .navbar {
        display: flex;
        justify-content: flex-start; /* Aligner à gauche pour le logo */
        align-items: center;
        background-color: black;
        padding: 12px 30px;
        border-bottom: 1px solid #333; /* Petite ligne grise en dessous */
        margin-bottom: 30px;
    }

    /* Lien de navigation */
    .navbar a {
        color: white;
        text-decoration: none;
        margin-right: 30px;
        font-size: 18px;
        font-weight: bold;
        text-transform: uppercase;
    }

    /* Survol (Couleur rouge du Code 1) */
    .navbar a:hover {
        color: #D7001D;
    }

    /* Logo image */
    .navbar img {
        height: 40px;
        margin-right: 40px;
    }

    /* Rendre les boutons Streamlit en rouge pour le style (optionnel) */
    div.stButton > button:first-child {
        background-color: #D7001D;
        color: white;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)


    # 2. Affichage de la Barre de Navigation (Avec Logo)
    st.markdown(
        f"""
    <div class="navbar">
        <a href="/">
            <img src="{logo_url_base64}" alt="Just Creuse It Logo">
        </a>
        <a href="/">Accueil</a>
        <a href="/Reco_Top_Films_at_Tim">Films</a>
        <a href="/Reco_Top_Actors_Films_at_Tim">Acteurs</a>
        <a href="/Reco_Top_Genrs_Films_at_Tim">Genres</a>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --- PAGE 1 : L'IMAGE POPCORN & LE TEXTE ---

    # On crée 2 colonnes : Image à gauche, Texte à droite
    col1, col2 = st.columns([1, 1], gap="medium")

    with col1:
        try:
            # st.image gère mieux les chemins locaux que le Base64 dans ce cas
            st.image(background_path, use_container_width=True)
        except FileNotFoundError:
            st.warning(f"⚠️ Image '{os.path.basename(background_path)}' introuvable.")
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement de l'image popcorn : {e}")

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
            # st.video gère mieux les chemins locaux
            st.video(scooby_path)
        except FileNotFoundError:
            st.warning(f"⚠️ Vidéo '{os.path.basename(scooby_path)}' introuvable.")
        except Exception as e:
            st.warning(f"⚠️ Erreur lors du chargement de la vidéo scooby : {e}")


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
            st.success(f"Recherche : **{search}**")


    st.markdown("<br><br>", unsafe_allow_html=True)