"""Authentification : hachage bcrypt et vérification des rôles."""

import bcrypt
import streamlit as st
from database import get_session
from models.user import User
from config import PERMISSIONS


def hash_password(password: str) -> str:
    """Chiffre un mot de passe avec bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Vérifie un mot de passe contre son hash bcrypt."""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def authenticate(username: str, password: str) -> dict | None:
    """
    Authentifie un utilisateur.
    Retourne un dict avec les infos user ou None si échec.
    """
    session = get_session()
    try:
        user = session.query(User).filter(
            User.username == username, User.actif == True  # noqa: E712
        ).first()
        if user and verify_password(password, user.password_hash):
            return {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "nom_complet": user.nom_complet or user.username,
                "enseignant_id": user.enseignant_id,
            }
        return None
    finally:
        session.close()


def login_user(user_data: dict):
    """Enregistre l'utilisateur connecté dans la session Streamlit."""
    st.session_state["authenticated"] = True
    st.session_state["user"] = user_data


def logout_user():
    """Déconnecte l'utilisateur."""
    for key in ["authenticated", "user", "current_page"]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict | None:
    return st.session_state.get("user")


def has_permission(module: str) -> bool:
    """Vérifie si l'utilisateur courant a accès au module."""
    user = get_current_user()
    if not user:
        return False
    allowed = PERMISSIONS.get(user["role"], [])
    return module in allowed


def require_auth():
    """Arrête l'exécution si l'utilisateur n'est pas connecté."""
    if not is_authenticated():
        st.warning("Veuillez vous connecter pour accéder à cette page.")
        st.stop()
