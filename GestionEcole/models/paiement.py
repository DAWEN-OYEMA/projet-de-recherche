"""Modèle Paiement."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Paiement(Base):
    __tablename__ = "paiements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)
    frais_id = Column(Integer, ForeignKey("frais_scolaires.id"), nullable=False)
    montant_paye = Column(Float, nullable=False)
    montant_total = Column(Float, nullable=False)
    reste = Column(Float, default=0.0)
    date_paiement = Column(DateTime, default=datetime.utcnow)
    reference = Column(String(50), unique=True)
    mode_paiement = Column(String(30), default="Espèces")
    caissier = Column(String(100))

    eleve = relationship("Eleve", back_populates="paiements")
    frais = relationship("FraisScolaire", back_populates="paiements")

    def __repr__(self):
        return f"<Paiement {self.reference} - {self.montant_paye}>"
