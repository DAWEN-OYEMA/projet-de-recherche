"""
Connexion SQLAlchemy et initialisation de la base de données MySQL.
Crée automatiquement la base et toutes les tables au premier lancement.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME

Base = declarative_base()

# Moteur sans base spécifique (pour créer la DB si elle n'existe pas)
_server_url = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}"
    f"?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database_if_not_exists():
    """Crée la base de données MySQL si elle n'existe pas encore."""
    temp_engine = create_engine(_server_url, pool_pre_ping=True)
    with temp_engine.connect() as conn:
        conn.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` "
                f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
        conn.commit()
    temp_engine.dispose()


def init_db():
    """Initialise la base : crée la DB, les tables et l'admin par défaut."""
    create_database_if_not_exists()

    # Importer les modèles pour enregistrer les métadonnées
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _seed_default_admin()


def _seed_default_admin():
    """Insère un administrateur par défaut si aucun utilisateur n'existe."""
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
    """Retourne une session SQLAlchemy (à fermer après usage)."""
    return SessionLocal()
