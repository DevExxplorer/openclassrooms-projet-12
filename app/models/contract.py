from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base

from app.models.date_tracked import DateTracked


class Contract(Base, DateTracked):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relation avec la class Client
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("Client", back_populates="contracts")

    # Relation avec la class User
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    commercial_contact = relationship("User", back_populates="contracts")

    # Informations complémentaires
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    is_signed = Column(Boolean, nullable=False, default=False)

    # Relation avec la class Event
    events = relationship("Event", back_populates="contract")

    def __repr__(self):
        return f"Contract(id={self.id}, client='{self.client.name if self.client else 'None'}', signed={self.is_signed})"

    def __str__(self):
        return f"Contrat #{self.id} - {self.client.name if self.client else 'Client inconnu'} ({'Signé' if self.is_signed else 'Non signé'})"