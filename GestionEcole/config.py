"""
Configuration de l'application.

- En local : MySQL (WampServer)
- Sur Streamlit Community Cloud : SQLite
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get(key: str, default: str = "") -> str:
    """Lit une variable depuis .env ou Streamlit Secrets."""
    value = os.getenv(key)
    if value:
        return value

    try:
        import streamlit as st

        if key in st.secrets:
            return str(st.secrets[key])

    except Exception:
        pass

    return default


# -------------------------------------------------
# Détection de l'environnement
# -------------------------------------------------

IS_STREAMLIT = (
    os.getenv("STREAMLIT_SERVER_PORT") is not None
    or os.getenv("STREAMLIT_RUNTIME") is not None
)

# -------------------------------------------------
# Paramètres MySQL (local)
# -------------------------------------------------

DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = _get("DB_PORT", "3306")
DB_USER = _get("DB_USER", "root")
DB_PASSWORD = _get("DB_PASSWORD", "")
DB_NAME = _get("DB_NAME", "gestion_ecole")

# -------------------------------------------------
# Choix automatique de la base de données
# -------------------------------------------------

if IS_STREAMLIT:
    DATABASE_URL = "sqlite:///gestion_ecole.db"
else:
    DATABASE_URL = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )

# -------------------------------------------------
# Application
# -------------------------------------------------

APP_TITLE = _get("APP_TITLE", "Gestion Scolaire")
APP_ICON = "🏫"
SCHOOL_NAME = _get("SCHOOL_NAME", "École Primaire Excellence")

# -------------------------------------------------
# Dossiers
# -------------------------------------------------

ASSETS_DIR = BASE_DIR / "assets"
PHOTOS_DIR = ASSETS_DIR / "photos"
EXPORTS_DIR = BASE_DIR / "exports"

PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# Rôles
# -------------------------------------------------

ROLE_ADMIN = "administrateur"
ROLE_ENSEIGNANT = "enseignant"
ROLE_CAISSIER = "caissier"

ROLES = {
    ROLE_ADMIN: "Administrateur",
    ROLE_ENSEIGNANT: "Enseignant",
    ROLE_CAISSIER: "Caissier",
}

PERMISSIONS = {
    ROLE_ADMIN: [
        "dashboard",
        "eleves",
        "enseignants",
        "classes",
        "cours",
        "paiements",
        "notes",
        "rapports",
        "utilisateurs",
    ],
    ROLE_ENSEIGNANT: [
        "dashboard",
        "eleves",
        "classes",
        "cours",
        "notes",
    ],
    ROLE_CAISSIER: [
        "dashboard",
        "eleves",
        "paiements",
        "rapports",
    ],
}
