from app.models.department import Department
from app.models.user import User
from app.database.db import db_manager


class Initialization:
    """Service d'initialisation de l'application"""
    @staticmethod
    def initialize_departments():
        """Initialiser les départements de base"""
        results = []

        for dept_name in Department.DEPARTMENTS:
            try:
                # Vérifier si le département existe
                session = db_manager.get_session()
                existing = session.query(Department).filter(Department.name == dept_name).first()
                session.close()

                if not existing:
                    department = Department.create(
                        name=dept_name,
                        description=f"Département {dept_name}"
                    )
                    results.append((department, True))
                else:
                    results.append((existing, False))

            except Exception as e:
                results.append((None, f"Erreur pour {dept_name}: {e}"))

        return results

    @staticmethod
    def create_default_admin():
        """Créer l'administrateur par défaut"""
        try:
            admin = User.create(
                name="Admin",
                mail="admin@epicevents.com",
                username="admin",
                password="admin123",
                department="gestion"
            )
            return admin, True
        except Exception as e:
            raise e

    @staticmethod
    def initialize_application():
        """Initialiser toute l'application"""
        results = {
            'departments': [],
            'admin': None,
            'errors': []
        }

        try:
            # Initialiser les départements
            dept_results = Initialization.initialize_departments()
            results['departments'] = dept_results

            # Créer l'admin
            admin, admin_created = Initialization.create_default_admin()
            results['admin'] = (admin, admin_created)

        except Exception as e:
            results['errors'].append(f"Erreur lors de l'initialisation: {e}")

        return results
