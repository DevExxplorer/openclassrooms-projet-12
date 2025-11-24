from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base, db_manager
from app.models.date_tracked import DateTracked
from app.utils.validators import validate_email, validate_tel
import sentry_sdk


class Client(Base, DateTracked):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    mail = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    company_name = Column(String(255))

    # Relation avec la class User (Equipe commercial)
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    commercial_contact = relationship("app.models.user.User", back_populates="clients")

    # Relation avec la class Contract
    contracts = relationship("app.models.contract.Contract", back_populates="client")

    def __repr__(self):  # pragma: no cover
        return f"Client(id={self.id}, name='{self.name}', email='{self.mail}', company='{self.company_name}')"

    def __str__(self):  # pragma: no cover
        created_str = self.created_at.strftime('%d/%m/%Y à %H:%M')
        updated_str = self.last_updated_at.strftime('%d/%m/%Y à %H:%M') if self.last_updated_at else 'Jamais modifié'
        return f"({self.id}) - {self.name} ({self.mail}) - {self.company_name}\nCréé: {created_str} | Modifié: {updated_str}"

    @classmethod
    def create(cls, role, **kwargs):
        """Création du client après validation des champs"""
        session = None

        try:
            session = db_manager.get_session()

            if not kwargs.get('name') or kwargs.get('name').strip() == '':
                raise ValueError("Le nom du client est obligatoire")

            # Validation des formats du mail et du téléphone
            if 'mail' in kwargs:
                validate_email(kwargs['mail'])
            if 'phone' in kwargs and kwargs['phone']:
                validate_tel(kwargs['phone'])

            #  Contrôle de permission
            if role != 'commercial':
                raise PermissionError("Seuls les commerciaux peuvent créer des clients")

            # Vérification de l'existence d'un client
            if 'mail' in kwargs:
                existing = session.query(cls).filter(cls.mail == kwargs['mail']).first()
                if existing:
                    raise ValueError(f"Le client avec l'email '{kwargs['mail']}' existe déjà")

            client = cls(**kwargs)
            session.add(client)
            session.commit()
            session.refresh(client)
            return client

        except Exception as e:
            if session:
                session.rollback()

            sentry_sdk.set_context("client_model_create", {
                "role": role,
                "action": "create_error",
                "client_data": kwargs,
                "error_type": type(e).__name__
            })

            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    def update(self, **kwargs):
        """Mettre à jour le client actuel"""
        session = None
        try:
            session = db_manager.get_session()
            client = session.merge(self)
            
            for key, value in kwargs.items():
                if hasattr(client, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(client, key, value)

            session.commit()
            session.refresh(client)
            
            # Mettre à jour l'instance actuelle
            for key, value in kwargs.items():
                if hasattr(self, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(self, key, value)
            return client

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
        """
        Récupérer tous les clients
        Accessible à tous les rôles selon le cahier des charges
        """
        session = None
        try:
            session = db_manager.get_session()
            clients = session.query(cls).all()
            return clients

        except Exception as e:  # pragma: no cover
            if session:
                session.rollback()

            sentry_sdk.set_context("client_model_get_all", {
                "action": "get_all_error",
                "error_type": type(e).__name__
            })

            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_id(cls, client_id):
        """
        Récupérer un client par son ID
        Accessible à tous les rôles
        """
        session = None
        try:
            session = db_manager.get_session()
            client = session.query(cls).filter(cls.id == client_id).first()
            if not client:
                raise ValueError(f"Client avec l'ID {client_id} introuvable")
            return client
        except Exception as e:
            if session:
                session.rollback()

            sentry_sdk.set_context("client_model_get_by_id", {
                "client_id": client_id,
                "action": "get_by_id_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_email(cls, email):
        """
        Récupérer un client par son email
        Accessible à tous les rôles
        """
        session = None
        try:
            session = db_manager.get_session()
            client = session.query(cls).filter(cls.mail == email).first()
            if not client:
                raise ValueError(f"Client avec l'email '{email}' introuvable")
            return client

        except Exception as e:
            if session:
                session.rollback()

            sentry_sdk.set_context("client_model_get_by_email", {
                "email": email,
                "action": "get_by_email_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_commercial(cls, user_id):
        """RÉCUPÉRER LES CLIENTS D'UN COMMERCIAL"""
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
    def search_by_name(cls, name):
        """RECHERCHER LES CLIENTS PAR NOM"""
        session = None
        try:
            session = db_manager.get_session()
            return session.query(cls).filter(cls.name.ilike(f"%{name}%")).all()
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_id_with_permissions(cls, client_id, user_id):
        """RÉCUPÉRER UN CLIENT AVEC PERMISSIONS"""
        session = None
        try:
            session = db_manager.get_session()
            client = session.query(cls).filter(
                cls.id == client_id,
                cls.commercial_contact_id == user_id
            ).first()
            return client
        except Exception as e:
            sentry_sdk.capture_exception(e)
            return None
        finally:
            if session:
                session.close()