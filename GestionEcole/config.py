"""
Configuration de l'application via variables d'environnement (.env).
Compatible WampServer (local) et Streamlit Community Cloud.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger le fichier .env depuis la racine du projet
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _get(key: str, default: str = "") -> str:
    """Lit une variable depuis os.environ ou st.secrets (Streamlit Cloud)."""
    value = os.getenv(key)
    if value:
        return value
    try:
        import streamlit as st
        return str(st.secrets.get(key, default))
    except Exception:
        return default


# ── Base de données MySQL ──────────────────────────────────────────
DB_HOST = _get("DB_HOST", "localhost")
DB_PORT = _get("DB_PORT", "3306")
DB_USER = _get("DB_USER", "root")
DB_PASSWORD = _get("DB_PASSWORD", "")
DB_NAME = _get("DB_NAME", "gestion_ecole")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset=utf8mb4"
)

# ── Application ────────────────────────────────────────────────────
APP_TITLE = _get("APP_TITLE", "Gestion Scolaire")
APP_ICON = "🏫"
SCHOOL_NAME = _get("SCHOOL_NAME", "École Primaire Excellence")

# ── Chemins ────────────────────────────────────────────────────────
ASSETS_DIR = BASE_DIR / "assets"
PHOTOS_DIR = ASSETS_DIR / "photos"
EXPORTS_DIR = BASE_DIR / "exports"

# Créer les dossiers s'ils n'existent pas
PHOTOS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Rôles utilisateur ──────────────────────────────────────────────
ROLE_ADMIN = "administrateur"
ROLE_ENSEIGNANT = "enseignant"
ROLE_CAISSIER = "caissier"

ROLES = {
    ROLE_ADMIN: "Administrateur",
    ROLE_ENSEIGNANT: "Enseignant",
    ROLE_CAISSIER: "Caissier",
}

# Permissions par module
PERMISSIONS = {
    ROLE_ADMIN: ["dashboard", "eleves", "enseignants", "classes", "cours",
                  "paiements", "notes", "rapports", "utilisateurs"],
    ROLE_ENSEIGNANT: ["dashboard", "eleves", "classes", "cours", "notes"],
    ROLE_CAISSIER: ["dashboard", "eleves", "paiements", "rapports"],
}
