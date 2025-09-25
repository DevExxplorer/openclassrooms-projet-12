from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base, db_manager
from app.models.client import Client
from app.models.user import User
from app.models.date_tracked import DateTracked


class Contract(Base, DateTracked):
    __tablename__ = 'contracts'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relation avec la class Client
    client_id = Column(Integer, ForeignKey('clients.id'), nullable=False)
    client = relationship("app.models.client.Client", back_populates="contracts")

    # Relation avec la class User
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    commercial_contact = relationship("app.models.user.User", back_populates="contracts")

    # Informations complémentaires
    total_amount = Column(Float, nullable=False)
    remaining_amount = Column(Float, nullable=False)
    is_signed = Column(Boolean, nullable=False, default=False)

    # Relation avec la class Event
    events = relationship("app.models.event.Event", back_populates="contract")

    def __repr__(self):  # pragma: no cover
        return f"Contract(id={self.id}, client='{self.client.name if self.client else 'None'}', signed={self.is_signed})"

    def __str__(self):  # pragma: no cover
        return f"Contrat #{self.id} - {self.client.name if self.client else 'Client inconnu'} ({'Signé' if self.is_signed else 'Non signé'})"

    def create(**kwargs):
        """Créer un nouveau contrat"""

        session = db_manager.get_session()

        # Vérification de l'existence du client
        client = session.query(Client).filter(Client.id == kwargs.get('client_id')).first()
        if not client:
            raise ValueError(f"Client avec l'ID {kwargs.get('client_id')} introuvable")
        
        # Vérification de l'existence du commercial
        commercial = session.query(User).filter(User.id == kwargs.get('commercial_contact_id')).first()
        if not commercial:
            raise ValueError(f"Commercial avec l'ID {kwargs.get('commercial_contact_id')} introuvable")
        
        # Création du contrat
        contract = Contract(
            client_id=kwargs.get('client_id'),
            commercial_contact_id=kwargs.get('commercial_contact_id'),
            total_amount=kwargs.get('total_amount'),
            remaining_amount=kwargs.get('remaining_amount'),
            is_signed=(kwargs.get('status') == 'signé')
        )
        session = db_manager.get_session()
        session.add(contract)
        session.commit()
        session.refresh(contract)
        session.close()
        return contract