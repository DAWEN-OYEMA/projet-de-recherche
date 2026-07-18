"""Modèle Classe."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Classe(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(50), unique=True, nullable=False)
    niveau = Column(String(50))
    titulaire_id = Column(Integer, ForeignKey("enseignants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    titulaire = relationship("Enseignant", back_populates="classes_titulaire")
    eleves = relationship("Eleve", back_populates="classe")
    cours = relationship("Cours", back_populates="classe")

    @property
    def effectif(self):
        return len([e for e in self.eleves if e.actif])

    def __repr__(self):
        return f"<Classe {self.nom}>"
