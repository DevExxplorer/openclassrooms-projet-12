from app.views.user import userView
from app.models.user import User
from rich.console import Console
from app.database.db import db_manager
from app.models.department import Department


class UserCommands:
    def __init__(self, current_user=None):
        self.user_view = userView()
        self.console = Console()
        self.current_user = current_user

    def create_user(self):
        """Créer un collaborateur"""
        user_data = self.user_view.get_user_creation_form()
        try:
            user = User.create(**user_data)
            self.console.print(f"[green]Collaborateur {user.name} créé ![green]")
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[red]")

    def update_user(self):
        """Modifier un collaborateur"""
        self.list_users()
        user_id = self.user_view.get_user_id()
        session = db_manager.get_session()

        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                self.console.print(f"[red]Collaborateur avec l'ID {user_id} introuvable.[/red]")
                return

            # Forcer le chargement du département avant de l'utiliser
            dept_name = user.department.name if user.department else None

            updated_data = self.user_view.get_user_update_form(user)

            # Gérer le département spécialement
            if 'department' in updated_data:
                new_dept_name = updated_data.pop('department')  # Retire 'department' du dict
                if new_dept_name != dept_name:  # Seulement si changement
                    dept = session.query(Department).filter(Department.name == new_dept_name).first()
                    if dept:
                        user.department_id = dept.id
                    else:
                        self.console.print(f"[red]Département '{new_dept_name}' introuvable.[/red]")
                        return

            # Gérer le mot de passe s'il est fourni
            if 'password' in updated_data and updated_data['password'].strip():
                password = updated_data.pop('password')
                user.password_hash = User.hash_password(password)
            elif 'password' in updated_data:
                updated_data.pop('password')  # Enlever si vide

            # Mettre à jour les autres champs
            for key, value in updated_data.items():
                if hasattr(user, key) and value.strip():  # Vérifier que l'attribut existe et n'est pas vide
                    setattr(user, key, value)

            session.commit()
            self.console.print(f"[green]Collaborateur {user.name} mis à jour avec succès ![/green]")

        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[/red]")
        finally:
            session.close()

    def delete_user(self):
        """Supprimer un collaborateur"""
        self.list_users()

        user_id = self.user_view.get_user_id()
        session = db_manager.get_session()

        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                self.console.print(f"[red]Collaborateur avec l'ID {user_id} introuvable.[/red]")
                return

            session.delete(user)
            session.commit()
            self.console.print(f"[green]Collaborateur {user.name} supprimé ![green]")
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur : {e}[red]")
        finally:
            session.close()

    def list_users(self, filter_by_department=None):
        """Lister tous les collaborateurs"""
        try:
            session = db_manager.get_session()
            try:
                if filter_by_department:
                    users = session.query(User).join(User.department).filter(
                        Department.name == filter_by_department
                    ).all()
                else:
                    users = session.query(User).all()

                # Forcer le chargement AVANT de fermer la session
                for user in users:
                    _ = user.department.name if user.department else None
            finally:
                session.close()

            self.user_view.display_user_list(users)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
