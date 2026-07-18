"""Modèle Frais Scolaire."""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from database import Base


class FraisScolaire(Base):
    __tablename__ = "frais_scolaires"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    montant = Column(Float, nullable=False)
    annee_scolaire = Column(String(10), default="2025-2026")
    description = Column(String(255))

    paiements = relationship("Paiement", back_populates="frais")

    def __repr__(self):
        return f"<FraisScolaire {self.nom} - {self.montant}>"
