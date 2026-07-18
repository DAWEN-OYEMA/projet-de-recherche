"""Interface utilisateur : CSS personnalisé, composants réutilisables."""

import streamlit as st
from config import APP_TITLE, SCHOOL_NAME


def load_css():
    """Injecte le CSS personnalisé pour un thème professionnel."""
    st.markdown("""
    <style>
    /* ── Variables ── */
    :root {
        --primary: #1e3a5f;
        --primary-light: #2c5282;
        --accent: #3182ce;
        --success: #38a169;
        --danger: #e53e3e;
        --warning: #d69e2e;
        --bg-card: #ffffff;
        --text-muted: #718096;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary) 0%, var(--primary-light) 100%);
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #ffffff !important;
    }

    /* ── Métriques KPI ── */
    div[data-testid="stMetric"] {
        background: var(--bg-card);
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    div[data-testid="stMetric"] label {
        color: var(--text-muted) !important;
        font-size: 0.85rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: var(--primary) !important;
        font-weight: 700 !important;
    }

    /* ── Cartes ── */
    .card {
        background: var(--bg-card);
        border-radius: 12px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #e2e8f0;
        margin-bottom: 16px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--primary);
        margin-bottom: 12px;
    }

    /* ── En-tête page ── */
    .page-header {
        background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
        color: white;
        padding: 20px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
    }
    .page-header h1 {
        margin: 0;
        font-size: 1.6rem;
        color: white !important;
    }
    .page-header p {
        margin: 4px 0 0 0;
        opacity: 0.85;
        color: white !important;
    }

    /* ── Login ── */
    .login-container {
        max-width: 420px;
        margin: 60px auto;
        padding: 40px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
    }
    .login-title {
        text-align: center;
        color: var(--primary);
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 8px;
    }
    .login-subtitle {
        text-align: center;
        color: var(--text-muted);
        margin-bottom: 32px;
    }

    /* ── Boutons ── */
    .stButton > button[kind="primary"] {
        background: var(--accent) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* ── Tableaux ── */
    .stDataFrame {
        border-radius: 8px;
        overflow: hidden;
    }

    /* ── Masquer le menu Streamlit par défaut ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* ── Badge rôle ── */
    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        background: rgba(255,255,255,0.2);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Affiche un en-tête de page stylisé."""
    st.markdown(f"""
    <div class="page-header">
        <h1>{icon} {title}</h1>
        {"<p>" + subtitle + "</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)


def show_success(message: str):
    st.success(f"✅ {message}")


def show_error(message: str):
    st.error(f"❌ {message}")


def show_warning(message: str):
    st.warning(f"⚠️ {message}")


def show_info(message: str):
    st.info(f"ℹ️ {message}")


def render_sidebar(user: dict, menu_items: list[tuple[str, str, str]]):
    """
    Affiche le menu latéral avec icônes.
    menu_items: liste de (key, label, icon)
    """
    with st.sidebar:
        st.markdown(f"## 🏫 {APP_TITLE}")
        st.markdown(f"<p style='color:rgba(255,255,255,0.7);font-size:0.85rem;'>{SCHOOL_NAME}</p>",
                    unsafe_allow_html=True)
        st.markdown("---")

        # Navigation
        labels = [f"{icon}  {label}" for _, label, icon in menu_items]
        keys = [key for key, _, _ in menu_items]

        if "current_page" not in st.session_state:
            st.session_state.current_page = keys[0]

        selected_label = st.radio(
            "Navigation",
            labels,
            index=keys.index(st.session_state.current_page) if st.session_state.current_page in keys else 0,
            label_visibility="collapsed",
        )
        selected_idx = labels.index(selected_label)
        st.session_state.current_page = keys[selected_idx]

        st.markdown("---")

        # Infos utilisateur
        role_labels = {
            "administrateur": "👑 Administrateur",
            "enseignant": "👨‍🏫 Enseignant",
            "caissier": "💰 Caissier",
        }
        st.markdown(f"**{user['nom_complet']}**")
        st.markdown(
            f"<span class='role-badge'>{role_labels.get(user['role'], user['role'])}</span>",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        if st.button("🚪 Déconnexion", use_container_width=True):
            from utils.auth import logout_user
            logout_user()
            st.rerun()

    return st.session_state.current_page


def kpi_row(metrics: list[tuple[str, str | int | float, str]]):
    """
    Affiche une rangée de KPI.
    metrics: liste de (label, value, icon)
    """
    cols = st.columns(len(metrics))
    for col, (label, value, icon) in zip(cols, metrics):
        with col:
            st.metric(label=f"{icon} {label}", value=value)
