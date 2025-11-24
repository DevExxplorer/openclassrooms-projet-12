import random
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.db import Base, db_manager
from app.models.date_tracked import DateTracked
from app.models.department import Department
import sentry_sdk


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

    def __repr__(self):  # pragma: no cover
        return (
            f"Client(id={self.id}, "
            f"employee_number='{self.employee_number}', "
            f"name='{self.name}', "
            f"mail='{self.mail}', "
            f"department='{self.department}')"
        )

    def __str__(self):  # pragma: no cover
        created_str = self.created_at.strftime('%d/%m/%Y à %H:%M')
        updated_str = self.last_updated_at.strftime('%d/%m/%Y à %H:%M') if self.last_updated_at else 'Jamais modifié'
        return (
            f"Client(id={self.id}, employee_number='{self.employee_number}', "
            f"name='{self.name}', mail='{self.mail}', department_id={self.department_id})\n"
            f"Créé: {created_str} | Modifié: {updated_str}"
        )

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
        session = None

        try:
            session = db_manager.get_session()
            user = session.query(cls).filter(cls.username == username).first()
            if user and user.verify_password(password):
                _ = user.department.name if user.department else None
                return user
            return None

        except Exception as e:
            sentry_sdk.set_context("user_model_authenticate", {
                "username": username,
                "action": "authenticate_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def create(cls, **kwargs):
        """Créer un nouvel utilisateur avec mot de passe haché"""
        session = None
        try:
            session = db_manager.get_session()

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
            if session:
                session.rollback()

            sentry_sdk.set_context("user_model_create", {
                "action": "create_error",
                "user_data": kwargs,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    def update(self, **kwargs):
        """Mettre à jour l'instance d'utilisateur actuelle"""
        session = None
        try:
            session = db_manager.get_session()
            user = session.merge(self)
            
            # Gestion du département
            if 'department' in kwargs:
                dept_name = kwargs.pop('department')
                dept = session.query(Department).filter(Department.name == dept_name).first()
                if dept:
                    user.department_id = dept.id
                else:
                    raise ValueError(f"Département '{dept_name}' introuvable")

            # Gestion du mot de passe
            if 'password' in kwargs and kwargs['password'].strip():
                password = kwargs.pop('password')
                user.password_hash = self.hash_password(password)
            elif 'password' in kwargs:
                kwargs.pop('password')

            # Mise à jour des autres champs
            for key, value in kwargs.items():
                if hasattr(user, key) and value and value.strip():
                    setattr(user, key, value)

            session.commit()
            session.refresh(user)
            
            # Mettre à jour l'instance actuelle
            for key, value in kwargs.items():
                if hasattr(self, key) and value and value.strip():
                    setattr(self, key, value)
            
            return user
        except Exception as e:
            if session:
                session.rollback()
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def delete(cls, user_id, role):
        """
        Supprimer un utilisateur
        Seule l'équipe gestion peut le faire
        """
        session = None
        try:
            session = db_manager.get_session()

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
            if session:
                session.rollback()
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_all(cls):
        """Récupérer tous les utilisateurs"""
        session = None
        try:
            session = db_manager.get_session()
            users = session.query(cls).all()
            return users

        except Exception as e:  # pragma: no cover
            if session:
                session.rollback()
            sentry_sdk.set_context("user_model_get_all", {
                "action": "get_all_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def _generate_employee_number(cls):
        """Générer un numéro d'employé unique"""
        session = None
        try:
            session = db_manager.get_session()

            while True:
                # Générer un numéro aléatoire à 4 chiffres
                random_number = random.randint(1000, 9999)
                employee_number = f"EMP{random_number}"

                existing = session.query(cls).filter(cls.employee_number == employee_number).first()

                if not existing:
                    return employee_number

        except Exception as e:
            sentry_sdk.set_context("user_model_generate_employee_number", {
                "action": "generate_employee_number_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @property
    def department_name(self):
        """Récupère le nom du département"""
        return self.department.name if self.department else None

    @classmethod
    def get_by_id(cls, user_id):
        """Récupère un utilisateur par son ID"""
        session = None

        try:
            session = db_manager.get_session()
            user = session.query(cls).filter(cls.id == user_id).first()
            if user:
                # Forcer le chargement de la relation department
                _ = user.department.name if user.department else None
            return user

        except Exception as e:
            sentry_sdk.set_context("user_model_get_by_id", {
                "user_id": user_id,
                "action": "get_by_id_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_by_department(cls, department_name):
        """Récupérer les utilisateurs par département"""
        session = None
        try:
            session = db_manager.get_session()
            users = session.query(cls).join(cls.department).filter(
                Department.name == department_name
            ).all()
            # Forcer le chargement des départements
            for user in users:
                _ = user.department.name if user.department else None
            return users
        except Exception as e:
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()
