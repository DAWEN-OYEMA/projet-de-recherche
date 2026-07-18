"""Package des modèles SQLAlchemy."""

from models.user import User
from models.eleve import Eleve
from models.enseignant import Enseignant, enseignant_matiere
from models.matiere import Matiere
from models.classe import Classe
from models.cours import Cours
from models.frais import FraisScolaire
from models.paiement import Paiement
from models.note import Note

__all__ = [
    "User", "Eleve", "Enseignant", "enseignant_matiere",
    "Matiere", "Classe", "Cours", "FraisScolaire", "Paiement", "Note",
]
