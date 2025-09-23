from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database.db import Base, db_manager


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
        session = db_manager.get_session()

        try:
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
            session.rollback()
            raise e
        finally:
            session.close()

    @classmethod
    def get_department_with_id(cls, department_id):
        """Récupère le nom du département via son ID"""
        session = db_manager.get_session()
        try:
            dept = session.query(cls).filter(cls.id == department_id).first()
            return dept.name if dept else None
        finally:
            session.close()
