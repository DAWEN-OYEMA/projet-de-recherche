"""Modèle Matière."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database import Base
from models.enseignant import enseignant_matiere


class Matiere(Base):
    __tablename__ = "matieres"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), unique=True, nullable=False)
    coefficient = Column(Integer, default=1)

    enseignants = relationship("Enseignant", secondary=enseignant_matiere, back_populates="matieres")
    cours = relationship("Cours", back_populates="matiere")
    notes = relationship("Note", back_populates="matiere")

    def __repr__(self):
        return f"<Matiere {self.nom}>"
