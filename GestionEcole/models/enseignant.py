"""Modèles Enseignant et table d'association enseignant-matière."""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime,
    ForeignKey, Table,
)
from sqlalchemy.orm import relationship
from database import Base

# Table d'association many-to-many
enseignant_matiere = Table(
    "enseignant_matiere",
    Base.metadata,
    Column("enseignant_id", Integer, ForeignKey("enseignants.id"), primary_key=True),
    Column("matiere_id", Integer, ForeignKey("matieres.id"), primary_key=True),
)


class Enseignant(Base):
    __tablename__ = "enseignants"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    postnom = Column(String(100))
    prenom = Column(String(100), nullable=False)
    telephone = Column(String(20))
    adresse = Column(String(255))
    salaire = Column(Float, default=0.0)
    actif = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)

    matieres = relationship("Matiere", secondary=enseignant_matiere, back_populates="enseignants")
    classes_titulaire = relationship("Classe", back_populates="titulaire")
    cours = relationship("Cours", back_populates="enseignant")
    user = relationship("User", back_populates="enseignant", uselist=False)

    @property
    def nom_complet(self):
        parts = [self.prenom, self.nom]
        if self.postnom:
            parts.insert(1, self.postnom)
        return " ".join(parts)

    def __repr__(self):
        return f"<Enseignant {self.nom_complet}>"
