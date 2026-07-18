"""
Application principale — Gestion Scolaire
Point d'entrée Streamlit avec authentification et navigation.
"""

import streamlit as st
from config import APP_TITLE, APP_ICON, PERMISSIONS
from database import init_db
from utils.auth import authenticate, login_user, is_authenticated, get_current_user
from utils.ui import load_css

# ── Configuration Streamlit ────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()


def show_login_page():
    """Affiche la page de connexion."""
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div class="login-container">
            <div class="login-title">🏫 Gestion Scolaire</div>
            <div class="login-subtitle">Connectez-vous pour accéder à l'application</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔒 Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter", type="primary",
                                               use_container_width=True)

            if submitted:
                if not username or not password:
                    st.error("Veuillez remplir tous les champs.")
                else:
                    user = authenticate(username, password)
                    if user:
                        login_user(user)
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects.")

        st.markdown("""
        <div style="text-align:center; color:#718096; font-size:0.8rem; margin-top:16px;">
            Compte par défaut : <b>admin</b> / <b>admin123</b>
        </div>
        """, unsafe_allow_html=True)


# ── Menu de navigation ─────────────────────────────────────────────
MENU_ITEMS = [
    ("dashboard", "Tableau de bord", "📊"),
    ("eleves", "Élèves", "👨‍🎓"),
    ("enseignants", "Enseignants", "👨‍🏫"),
    ("classes", "Classes", "🏛️"),
    ("cours", "Cours", "📚"),
    ("paiements", "Paiements", "💰"),
    ("notes", "Notes", "📝"),
    ("rapports", "Rapports", "📑"),
]

PAGE_MODULES = {
    "dashboard": "pages.dashboard",
    "eleves": "pages.eleves",
    "enseignants": "pages.enseignants",
    "classes": "pages.classes",
    "cours": "pages.cours",
    "paiements": "pages.paiements",
    "notes": "pages.notes",
    "rapports": "pages.rapports",
}


def main():
    # Initialiser la base de données au premier lancement
    if "db_initialized" not in st.session_state:
        try:
            init_db()
            st.session_state.db_initialized = True
        except Exception as e:
            st.error(f"Erreur de connexion à la base de données : {e}")
            st.info(
                "Vérifiez que MySQL (WampServer) est démarré et que les "
                "paramètres dans le fichier `.env` sont corrects."
            )
            st.stop()

    # Authentification
    if not is_authenticated():
        show_login_page()
        return

    user = get_current_user()
    allowed = PERMISSIONS.get(user["role"], [])

    # Filtrer le menu selon les permissions
    filtered_menu = [(k, l, i) for k, l, i in MENU_ITEMS if k in allowed]

    from utils.ui import render_sidebar
    current_page = render_sidebar(user, filtered_menu)

    # Charger et afficher la page sélectionnée
    if current_page in PAGE_MODULES:
        import importlib
        module = importlib.import_module(PAGE_MODULES[current_page])
        module.render()
    else:
        st.warning("Page non accessible.")


if __name__ == "__main__":
    main()
