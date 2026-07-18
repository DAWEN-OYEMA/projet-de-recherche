"""Modèle Note."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    eleve_id = Column(Integer, ForeignKey("eleves.id"), nullable=False)
    matiere_id = Column(Integer, ForeignKey("matieres.id"), nullable=False)
    note = Column(Float, nullable=False)
    coefficient = Column(Integer, default=1)
    type_evaluation = Column(String(30), default="Devoir")  # Devoir, Examen, Interrogation
    periode = Column(String(20), default="1er Trimestre")
    date_saisie = Column(DateTime, default=datetime.utcnow)

    eleve = relationship("Eleve", back_populates="notes")
    matiere = relationship("Matiere", back_populates="notes")

    def __repr__(self):
        return f"<Note {self.eleve_id} - {self.note}/{20}>"
