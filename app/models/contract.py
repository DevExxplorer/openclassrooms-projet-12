from sqlalchemy import Column, Integer, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base, db_manager
from app.models.client import Client
from app.models.user import User
from app.models.date_tracked import DateTracked
import sentry_sdk


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

    @classmethod
    def create(cls, **kwargs):
        """Créer un nouveau contrat"""
        session = None

        try:
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
            contract = cls(
                client_id=kwargs.get('client_id'),
                commercial_contact_id=kwargs.get('commercial_contact_id'),
                total_amount=kwargs.get('total_amount'),
                remaining_amount=kwargs.get('remaining_amount'),
                is_signed=(kwargs.get('status') == 'signé')
            )

            session.add(contract)
            session.commit()
            session.refresh(contract)
            return contract

        except Exception as e:
            if session:
                session.rollback()

            # Contexte Sentry pour l'erreur
            sentry_sdk.set_context("contract_model_create", {
                "action": "create_error",
                "contract_data": kwargs,
                "client_id": kwargs.get('client_id'),
                "commercial_contact_id": kwargs.get('commercial_contact_id'),
                "error_type": type(e).__name__
            })

            # Capturer l'exception avec Sentry
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_client_with_commercial(cls, client_id):
        """Récupérer le client et son commercial assigné"""
        session = None
        try:
            session = db_manager.get_session()
            client = session.query(Client).filter(Client.id == client_id).first()
            return client
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
        finally:
            if session:
                session.close()

    def update(self, **kwargs):
        """Mettre à jour un contrat existant"""
        session = None
        try:
            session = db_manager.get_session()
            contract = session.merge(self)

            for key, value in kwargs.items():
                if hasattr(contract, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(contract, key, value)

            session.commit()
            session.refresh(contract)

            # Mettre à jour l'instance actuelle
            for key, value in kwargs.items():
                if hasattr(self, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(self, key, value)
            return contract

        except Exception as e:
            if session:
                session.rollback()
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_all(cls):
        """Récupérer tous les contrats"""
        session = None
        try:
            session = db_manager.get_session()
            return session.query(cls).all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_commercial(cls, user_id):
        """Récupérer les contrats d'un commercial"""
        session = None
        try:
            session = db_manager.get_session()
            return session.query(cls).filter(cls.commercial_contact_id == user_id).all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_id_with_permissions(cls, contract_id, user_id, role):
        """Récupérer un contrat avec permissions"""
        session = None
        try:
            session = db_manager.get_session()
            
            if role == "commercial":
                contract = session.query(cls).join(cls.client).filter(
                    cls.id == contract_id,
                    Client.commercial_contact_id == user_id
                ).first()
            elif role == "gestion":
                contract = session.query(cls).filter(cls.id == contract_id).first()
            else:
                return None
                
            return contract
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
        finally:
            if session:
                session.close()

    @classmethod
    def get_filtered_contracts(cls, user_id, filter_type):
        """Filtrer les contrats d'un commercial"""
        session = None
        try:
            session = db_manager.get_session()
            
            base_query = session.query(cls).filter(cls.commercial_contact_id == user_id)
            
            if filter_type == "unsigned":
                return base_query.filter(~cls.is_signed).all()
            elif filter_type == "signed":
                return base_query.filter(cls.is_signed).all()
            elif filter_type == "unpaid":
                return base_query.filter(cls.remaining_amount > 0).all()
            
            return base_query.all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def validate_client_access(cls, client_id):
        """Valider l'accès au client"""
        session = None
        try:
            session = db_manager.get_session()
            client = session.query(Client).filter(Client.id == client_id).first()
            return client is not None
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return False
        finally:
            if session:
                session.close()
