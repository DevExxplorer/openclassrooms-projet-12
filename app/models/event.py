from sqlalchemy import Column, Integer, DateTime, String, Text, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from app.database.db import Base, db_manager
from app.models.date_tracked import DateTracked
from app.models.contract import Contract
from app.models.user import User
from app.models.department import Department
from app.models.client import Client
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

    def update(self, **kwargs):
        """Mettre à jour l'événement actuel"""
        session = None
        try:
            session = db_manager.get_session()

            # Merge l'objet dans la session courante
            event = session.merge(self)

            # Mise à jour des attributs
            for key, value in kwargs.items():
                if hasattr(event, key) and value is not None:
                    # Ignorer les chaînes vides
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(event, key, value)

            session.commit()
            session.refresh(event)

            # Mettre à jour l'instance actuelle
            for key, value in kwargs.items():
                if hasattr(self, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(self, key, value)
            return event

        except Exception as e:
            if session:
                session.rollback()
            sentry_sdk.set_context("event_model_update", {
                "action": "update_error",
                "event_id": self.id,
                "update_data": kwargs,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

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

    @classmethod
    def get_events_without_support(cls):
        """Récupérer les événements sans support assigné"""
        session = None
        try:
            session = db_manager.get_session()
            return session.query(cls).options(
                joinedload(cls.contract).joinedload(Contract.client),
                joinedload(cls.support_contact)
            ).filter(cls.support_contact_id.is_(None)).all()
        except Exception as e:
            sentry_sdk.set_context("event_model_get_no_support", {
                "action": "get_without_support_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    def assign_support(self, support_user_id):
        """Assigner un support à l'événement"""
        return self.update(support_contact_id=support_user_id)

    @classmethod
    def get_by_id(cls, event_id):
        """Récupérer un événement par son ID"""
        session = None
        try:
            session = db_manager.get_session()
            event = session.query(cls).options(
                joinedload(cls.contract).joinedload(Contract.client),
                joinedload(cls.support_contact)
            ).filter(cls.id == event_id).first()
            if not event:
                raise ValueError(f"Événement avec l'ID {event_id} introuvable")
            return event
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_available_supports(cls):
        """Récupérer la liste des supports disponibles"""
        session = None
        try:
            session = db_manager.get_session()
            supports = session.query(User).join(User.department).filter(
                Department.name == 'support'
            ).all()
            return supports
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def validate_support_user(cls, support_id):
        """Valider qu'un utilisateur est bien un support"""
        session = None
        try:
            session = db_manager.get_session()
            support = session.query(User).join(User.department).filter(
                User.id == support_id,
                Department.name == 'support'
            ).first()
            return support
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
        finally:
            if session:
                session.close()

    @classmethod
    def get_all(cls):
        """Récupérer tous les événements"""
        session = None
        try:
            session = db_manager.get_session()
            return session.query(cls).options(
                joinedload(cls.contract).joinedload(Contract.client),
                joinedload(cls.support_contact)
            ).all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_support_user(cls, user_id):
        """Récupérer les événements assignés à un utilisateur support"""
        session = None
        try:
            session = db_manager.get_session()
            return session.query(cls).options(
                joinedload(cls.contract).joinedload(Contract.client),
                joinedload(cls.support_contact)
            ).filter(cls.support_contact_id == user_id).all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def validate_contract_access(cls, contract_id, user_id):
        """Valider que l'utilisateur a accès au contrat"""
        session = None
        try:
            session = db_manager.get_session()
            contract = session.query(Contract).join(Contract.client).filter(
                Contract.id == contract_id,
                Contract.is_signed,
                Client.commercial_contact_id == user_id
            ).first()
            return contract is not None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False
        finally:
            if session:
                session.close()

    @classmethod
    def get_event_with_permissions(cls, event_id, user_id, user_role):
        """Récupérer un événement avec validation des permissions"""
        session = None
        try:
            session = db_manager.get_session()

            base_query = session.query(cls).options(
                joinedload(cls.contract).joinedload(Contract.client),
                joinedload(cls.support_contact)
            )

            if user_role == "support":
                event = base_query.filter(
                    cls.id == event_id,
                    cls.support_contact_id == user_id
                ).first()
            elif user_role == "gestion":
                event = base_query.filter(cls.id == event_id).first()
            else:
                return None

            return event
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
        finally:
            if session:
                session.close()
