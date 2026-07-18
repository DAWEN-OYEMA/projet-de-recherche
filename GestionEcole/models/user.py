"""Modèle Utilisateur — authentification et rôles."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="enseignant")
    nom_complet = Column(String(150))
    email = Column(String(100))
    actif = Column(Boolean, default=True)
    enseignant_id = Column(Integer, ForeignKey("enseignants.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    enseignant = relationship("Enseignant", back_populates="user", uselist=False)

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
