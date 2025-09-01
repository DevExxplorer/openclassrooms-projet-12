from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base, db_manager
from app.models.contract import Contract
from app.models.date_tracked import DateTracked
from app.models.user import User
from app.utils.validators import validate_email, validate_tel


class Client(Base, DateTracked):
    __tablename__ = 'clients'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    mail = Column(String(255), unique=True, nullable=False)
    phone = Column(String(50))
    company_name = Column(String(255))

    # Relation avec la class User (Equipe commercial)
    commercial_contact_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    commercial_contact = relationship(User, back_populates="clients")

    # Relation avec la class Contract
    contracts = relationship(Contract, back_populates="client")

    def __repr__(self): # pragma: no cover
        return f"Client(id={self.id}, name='{self.name}', email='{self.mail}', company='{self.company_name}')"

    def __str__(self): # pragma: no cover
        created_str = self.created_at.strftime('%d/%m/%Y à %H:%M')
        updated_str = self.last_updated_at.strftime('%d/%m/%Y à %H:%M') if self.last_updated_at else 'Jamais modifié'
        return f"({self.id}) - {self.name} ({self.mail}) - {self.company_name}\nCréé: {created_str} | Modifié: {updated_str}"

    @classmethod
    def create(cls, role, **kwargs):
        """
         Création du client après validation des champs
         """
        session = db_manager.get_session()

        try:
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
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_all(cls, role=None):
        """
        Récupérer tous les clients
        Accessible à tous les rôles selon le cahier des charges
        """
        session = db_manager.get_session()

        try:
            clients = session.query(cls).all()
            return clients
        except Exception as e: # pragma: no cover
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_by_id(cls, client_id, role=None):
        """
        Récupérer un client par son ID
        Accessible à tous les rôles
        """
        session = db_manager.get_session()

        try:
            client = session.query(cls).filter(cls.id == client_id).first()
            if not client:
                raise ValueError(f"Client avec l'ID {client_id} introuvable")
            return client
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_by_email(cls, email, role=None):
        """
        Récupérer un client par son email
        Accessible à tous les rôles
        """
        session = db_manager.get_session()

        try:
            client = session.query(cls).filter(cls.mail == email).first()
            if not client:
                raise ValueError(f"Client avec l'email '{email}' introuvable")
            return client
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
