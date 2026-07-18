"""Modèle Élève."""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from database import Base


class Eleve(Base):
    __tablename__ = "eleves"

    id = Column(Integer, primary_key=True, autoincrement=True)
    matricule = Column(String(20), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    postnom = Column(String(100))
    prenom = Column(String(100), nullable=False)
    sexe = Column(Enum("M", "F", name="sexe_enum"), nullable=False)
    date_naissance = Column(Date)
    adresse = Column(String(255))
    telephone = Column(String(20))
    parent = Column(String(150))
    photo = Column(String(255))
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    actif = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    classe = relationship("Classe", back_populates="eleves")
    paiements = relationship("Paiement", back_populates="eleve", cascade="all, delete-orphan")
    notes = relationship("Note", back_populates="eleve", cascade="all, delete-orphan")

    @property
    def nom_complet(self):
        parts = [self.prenom, self.nom]
        if self.postnom:
            parts.insert(1, self.postnom)
        return " ".join(parts)

    def __repr__(self):
        return f"<Eleve {self.matricule} - {self.nom_complet}>"
