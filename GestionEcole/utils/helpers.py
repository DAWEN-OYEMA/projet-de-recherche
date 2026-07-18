"""Fonctions utilitaires diverses."""

import uuid
from datetime import datetime, date
import pandas as pd
from pathlib import Path
from config import PHOTOS_DIR, EXPORTS_DIR


def generate_matricule(prefix: str = "ELV") -> str:
    """Génère un matricule unique."""
    year = datetime.now().strftime("%y")
    uid = uuid.uuid4().hex[:6].upper()
    return f"{prefix}{year}{uid}"


def generate_reference(prefix: str = "PAY") -> str:
    """Génère une référence de paiement unique."""
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{ts}"


def save_photo(uploaded_file, matricule: str) -> str | None:
    """Sauvegarde une photo uploadée et retourne le chemin relatif."""
    if uploaded_file is None:
        return None
    ext = Path(uploaded_file.name).suffix or ".jpg"
    filename = f"{matricule}{ext}"
    filepath = PHOTOS_DIR / filename
    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(filepath)


def df_to_excel(df: pd.DataFrame, filename: str) -> Path:
    """Exporte un DataFrame vers Excel dans le dossier exports/."""
    filepath = EXPORTS_DIR / filename
    df.to_excel(filepath, index=False, engine="openpyxl")
    return filepath


def read_excel(uploaded_file) -> pd.DataFrame:
    """Lit un fichier Excel uploadé."""
    return pd.read_excel(uploaded_file, engine="openpyxl")


def format_currency(amount: float) -> str:
    """Formate un montant en devise."""
    return f"{amount:,.0f} FC".replace(",", " ")


def format_date(d: date | datetime | None) -> str:
    """Formate une date en dd/mm/yyyy."""
    if d is None:
        return "—"
    if isinstance(d, datetime):
        d = d.date()
    return d.strftime("%d/%m/%Y")


def calculate_moyenne(notes: list) -> float:
    """Calcule la moyenne pondérée des notes."""
    if not notes:
        return 0.0
    total = sum(n.note * n.coefficient for n in notes)
    coefs = sum(n.coefficient for n in notes)
    return round(total / coefs, 2) if coefs else 0.0


def get_mention(moyenne: float) -> str:
    """Retourne la mention selon la moyenne /20."""
    if moyenne >= 16:
        return "Très Bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez Bien"
    elif moyenne >= 10:
        return "Passable"
    return "Insuffisant"


def search_filter_df(df: pd.DataFrame, query: str, columns: list[str]) -> pd.DataFrame:
    """Filtre un DataFrame par recherche instantanée sur plusieurs colonnes."""
    if not query:
        return df
    mask = pd.Series(False, index=df.index)
    for col in columns:
        if col in df.columns:
            mask |= df[col].astype(str).str.contains(query, case=False, na=False)
    return df[mask]
