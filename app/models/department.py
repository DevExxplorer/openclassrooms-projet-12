from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base, db_manager
import sentry_sdk


class Department(Base):
    DEPARTMENTS = ["commercial", "support", "gestion"]
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    description = Column(String(255))

    # Relations
    users = relationship("app.models.user.User", back_populates="department")

    @classmethod
    def create(cls, **kwargs):
        """Créer un nouveau département"""
        session = None

        try:
            session = db_manager.get_session()

            if 'name' in kwargs:
                if kwargs['name'] not in cls.DEPARTMENTS:
                    raise ValueError(f"Nom de département invalide. Doit être : {', '.join(cls.DEPARTMENTS)}")
            else:
                raise ValueError("Le nom du département est obligatoire")

            department = cls(**kwargs)
            session.add(department)
            session.commit()
            session.refresh(department)
            return department
        except Exception as e:
            if session:
                session.rollback()

            sentry_sdk.set_context("department_model_create", {
                "action": "create_error",
                "department_data": kwargs,
                "valid_departments": cls.DEPARTMENTS,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()

    @classmethod
    def get_department_with_id(cls, department_id):
        """Récupère le nom du département via son ID"""
        session = None

        try:
            session = db_manager.get_session()
            dept = session.query(cls).filter(cls.id == department_id).first()
            return dept.name if dept else None

        except Exception as e:
            sentry_sdk.set_context("department_model_get_by_id", {
                "department_id": department_id,
                "action": "get_by_id_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
        finally:
            if session:
                session.close()
