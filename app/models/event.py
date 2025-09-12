from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base
from app.models.date_tracked import DateTracked


class Event(Base, DateTracked):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    # Relation avec la class Contract
    contract_id = Column(Integer, ForeignKey('contracts.id'), nullable=False)
    contract = relationship("app.models.contract.Contract", back_populates="events")

    # Date de l'événement
    date_start = Column(DateTime, nullable=False)
    date_end = Column(DateTime, nullable=False)

    # Relation avec la class User
    support_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    support_contact = relationship("app.models.user.User", back_populates="events")

    # Détails de l'évenement
    location = Column(Text, nullable=False)
    attendees = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"Event(id={self.id}, name='{self.name}', client='{self.contract.client.name if self.contract and self.contract.client else 'None'}')"

    def __str__(self):
        return f"{self.name} - {self.contract.client.name if self.contract and self.contract.client else 'Client inconnu'}"
