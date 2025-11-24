from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base, db_manager
from app.models.date_tracked import DateTracked
from app.models.contract import Contract
from app.models.user import User
import sentry_sdk


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

    def __repr__(self):  # pragma: no cover
        return f"Event(id={self.id}, name='{self.name}', client='{self.contract.client.name if self.contract and self.contract.client else 'None'}')"

    def __str__(self):  # pragma: no cover
        return f"{self.name} - {self.contract.client.name if self.contract and self.contract.client else 'Client inconnu'}"

    @classmethod
    def create(cls, **kwargs):
        """Créer un nouvel événement"""
        session = None

        try:
            session = db_manager.get_session()

            # Vérification de l'existence du contrat
            contract = session.query(Contract).filter(Contract.id == kwargs.get('contract_id')).first()
            if not contract:
                raise ValueError(f"Contrat avec l'ID {kwargs.get('contract_id')} introuvable")

            # Vérification de l'existence du support (optionnel)
            support_contact = None
            if kwargs.get('support_contact_id'):
                support_contact = session.query(User).filter(User.id == kwargs.get('support_contact_id')).first()
                if not support_contact:
                    raise ValueError(f"Support avec l'ID {kwargs.get('support_contact_id')} introuvable")

            # Création de l'événement
            event = cls(
                name=kwargs.get('name'),
                contract_id=kwargs.get('contract_id'),
                date_start=kwargs.get('date_start'),
                date_end=kwargs.get('date_end'),
                support_contact_id=kwargs.get('support_contact_id') if support_contact else None,
                location=kwargs.get('location'),
                attendees=kwargs.get('attendees'),
                notes=kwargs.get('notes')
            )
            session.add(event)
            session.commit()
            session.refresh(event)

            return event

        except Exception as e:
            if session:
                session.rollback()

            sentry_sdk.set_context("event_model_create", {
                "action": "create_error",
                "event_data": kwargs,
                "contract_id": kwargs.get('contract_id'),
                "support_contact_id": kwargs.get('support_contact_id'),
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()
