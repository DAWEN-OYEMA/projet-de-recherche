"""Modèle Cours (emploi du temps)."""

from sqlalchemy import Column, Integer, String, Time, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Cours(Base):
    __tablename__ = "cours"

    id = Column(Integer, primary_key=True, autoincrement=True)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    enseignant_id = Column(Integer, ForeignKey("enseignants.id"), nullable=False)
    classe_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    jour = Column(String(15), nullable=False)  # Lundi, Mardi, ...
    heure_debut = Column(Time, nullable=False)
    heure_fin = Column(Time, nullable=False)
    salle = Column(String(50))

    matiere = relationship("Matiere", back_populates="cours")
    enseignant = relationship("Enseignant", back_populates="cours")
    classe = relationship("Classe", back_populates="cours")

    def __repr__(self):
        return f"<Cours {self.matiere.nom if self.matiere else '?'} - {self.jour}>"
