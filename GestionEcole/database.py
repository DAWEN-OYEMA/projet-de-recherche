"""
Connexion SQLAlchemy et initialisation de la base de données.

- En local : MySQL (WampServer)
- Sur Streamlit Community Cloud : SQLite
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import (
    DATABASE_URL,
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME,
)

Base = declarative_base()

# -------------------------------------------------------------------
# Création du moteur SQLAlchemy
# -------------------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# -------------------------------------------------------------------
# URL du serveur MySQL (sans sélectionner une base)
# Utilisée uniquement en local.
# -------------------------------------------------------------------

_server_url = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    "?charset=utf8mb4"
)


def create_database_if_not_exists():
    """
    Crée automatiquement la base MySQL si elle n'existe pas.

    Cette fonction est ignorée lorsque SQLite est utilisé.
    """

    if DATABASE_URL.startswith("sqlite"):
        return

    temp_engine = create_engine(
        _server_url,
        pool_pre_ping=True,
    )

    with temp_engine.connect() as conn:
        conn.execute(
            text(
                f"""
                CREATE DATABASE IF NOT EXISTS `{DB_NAME}`
                CHARACTER SET utf8mb4
                COLLATE utf8mb4_unicode_ci
                """
            )
        )
        conn.commit()

    temp_engine.dispose()


def init_db():
    """
    Initialise la base de données.
    """

    if DATABASE_URL.startswith("mysql"):
        create_database_if_not_exists()

    # Charger tous les modèles
    import models  # noqa: F401

    # Création automatique des tables
    Base.metadata.create_all(bind=engine)

    # Création du compte administrateur
    _seed_default_admin()


def _seed_default_admin():
    """
    Crée un administrateur par défaut si aucun utilisateur n'existe.
    """

    from models.user import User
    from utils.auth import hash_password

    session = SessionLocal()

    try:

        if session.query(User).count() == 0:

            admin = User(
                username="admin",
                password_hash=hash_password("admin123"),
                role="administrateur",
                nom_complet="Administrateur",
                actif=True,
            )

            session.add(admin)
            session.commit()

    finally:
        session.close()


def get_session():
    """
    Retourne une session SQLAlchemy.
    """

    return SessionLocal()
