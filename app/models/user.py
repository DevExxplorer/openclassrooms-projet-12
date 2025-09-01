from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base


class User(Base):
    DEPARTMENTS = ["commercial", "support", "gestion"]
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    mail = Column(String(255), unique=True, nullable=False)
    department = Column(String(50), nullable=False)

    # Pour l'authentification
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Un commercial peut avoir plusieurs clients
    clients = relationship("Client", back_populates="commercial_contact")

    # Un commercial peut avoir plusieurs contrats
    contracts = relationship("Contract", back_populates="commercial_contact")

    # Un membre du support peut avoir plusieurs événements assignés
    events = relationship("Event", back_populates="support_contact")

