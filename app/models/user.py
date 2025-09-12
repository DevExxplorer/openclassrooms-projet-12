import random

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.database.db import Base, db_manager
from app.models.date_tracked import DateTracked
from app.models.department import Department


class User(Base, DateTracked):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_number = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    mail = Column(String(255), unique=True, nullable=False)

    # Department
    department_id = Column(Integer, ForeignKey('departments.id'))
    department = relationship("app.models.department.Department", back_populates="users")

    # Pour l'authentification
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Un commercial peut avoir plusieurs clients
    clients = relationship("app.models.client.Client", back_populates="commercial_contact")

    # Un commercial peut avoir plusieurs contrats
    contracts = relationship("app.models.contract.Contract", back_populates="commercial_contact")

    # Un membre du support peut avoir plusieurs événements assignés
    events = relationship("app.models.event.Event", back_populates="support_contact")

    def __repr__(self): # pragma: no cover
        return f"Client(id={self.id}, employee_number='{self.employee_number}', name='{self.name}', mail='{self.mail}', department='{self.department}')"

    def __str__(self): # pragma: no cover
        created_str = self.created_at.strftime('%d/%m/%Y à %H:%M')
        updated_str = self.last_updated_at.strftime('%d/%m/%Y à %H:%M') if self.last_updated_at else 'Jamais modifié'
        return f"Client(id={self.id}, employee_number='{self.employee_number}', name='{self.name}', mail='{self.mail}', department_id={self.department_id})\nCréé: {created_str} | Modifié: {updated_str}"

    @staticmethod
    def hash_password(password):
        """Hacher le mot de passe avec salt automatique"""
        ph = PasswordHasher()
        return ph.hash(password)

    def verify_password(self, password):
        """Vérifier le mot de passe"""
        ph = PasswordHasher()
        try:
            ph.verify(self.password_hash, password)
            return True
        except VerifyMismatchError:
            return False

    @classmethod
    def authenticate(cls, username, password):
        """Authentifier un utilisateur"""
        session = db_manager.get_session()
        try:
            user = session.query(cls).filter(cls.username == username).first()
            if user and user.verify_password(password):
                return user
            return None
        finally:
            session.close()

    @classmethod
    def create(cls, **kwargs):
        """Créer un nouvel utilisateur avec mot de passe haché"""
        session = db_manager.get_session()

        try:
            # Générer automatiquement le numéro d'employé
            kwargs['employee_number'] = cls._generate_employee_number()

            # Validation du département
            if 'department' in kwargs:
                dept_name = kwargs.pop('department')
                dept = session.query(Department).filter(Department.name == dept_name).first()
                if not dept:
                    raise ValueError(f"Département '{dept_name}' introuvable")
                kwargs['department_id'] = dept.id

            # Hacher le mot de passe AVANT de créer l'utilisateur
            if 'password' in kwargs:
                password = kwargs.pop('password')
                kwargs['password_hash'] = cls.hash_password(password)
            else:
                raise ValueError("Le mot de passe est obligatoire")

            # Créer l'utilisateur avec le mot de passe haché
            user = cls(**kwargs)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def update(cls, user_id, role, **kwargs):
        """
        Mettre à jour un utilisateur
        Seul l'equipe de gestion peut modifier un utilisateur
        """
        session = db_manager.get_session()

        try:
            # Contrôle de permission
            if role != 'gestion':
                raise PermissionError("Seule l'équipe gestion peut modifier les utilisateurs")

            user = session.query(cls).filter(cls.id == user_id).first()
            if not user:
                raise ValueError(f"Utilisateur avec l'ID {user_id} introuvable")

            # Gestion du département si fourni
            if 'department' in kwargs:
                dept_name = kwargs.pop('department')
                dept = session.query(Department).filter(Department.name == dept_name).first()
                if not dept:
                    raise ValueError(f"Département '{dept_name}' introuvable")
                kwargs['department_id'] = dept.id

            # Hachage du nouveau mot de passe si fourni
            if 'password' in kwargs:
                password = kwargs.pop('password')
                kwargs['password_hash'] = cls.hash_password(password)

            # Mise à jour des champs
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            session.commit()
            session.refresh(user)
            return user

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def delete(cls, user_id, role):
        """
        Supprimer un utilisateur
        Seule l'équipe gestion peut le faire
        """
        session = db_manager.get_session()

        try:
            # Contrôle de permission
            if role != 'gestion':
                raise PermissionError("Seule l'équipe gestion peut supprimer les utilisateurs")

            user = session.query(cls).filter(cls.id == user_id).first()
            if not user:
                raise ValueError(f"Utilisateur avec l'ID {user_id} introuvable")

            session.delete(user)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_all(cls):
        """Récupérer tous les utilisateurs"""
        session = db_manager.get_session()

        try:
            users = session.query(cls).all()
            return users
        except Exception as e: # pragma: no cover
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def _generate_employee_number(cls):
        """Générer un numéro d'employé unique"""
        session = db_manager.get_session()

        try:
            while True:
                # Générer un numéro aléatoire à 4 chiffres
                random_number = random.randint(1000, 9999)
                employee_number = f"EMP{random_number}"

                existing = session.query(cls).filter(cls.employee_number == employee_number).first()

                if not existing:
                    return employee_number

        finally:
            session.close()