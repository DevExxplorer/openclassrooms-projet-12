from app.views.user import userView
from app.models.user import User
from rich.console import Console
from app.database.db import db_manager
from app.models.department import Department
import sentry_sdk


class UserCommands:
    def __init__(self, current_user=None):
        self.user_view = userView()
        self.console = Console()
        self.current_user = current_user

    def create_user(self):
        """Créer un collaborateur"""
        while True:
            try:
                user_data = self.user_view.get_user_creation_form()

                # Validation des champs requis
                required_fields = ['name', 'mail', 'password']
                missing_fields = []

                for field in required_fields:
                    if field not in user_data or not user_data[field] or not user_data[field].strip():
                        missing_fields.append(field)

                if missing_fields:
                    self.console.print(f"[red]Les champs suivants sont requis : {', '.join(missing_fields)}[/red]")
                    continue

                # Validation de l'email
                if '@' not in user_data['mail']:
                    self.console.print("[red]L'adresse email n'est pas valide[/red]")
                    continue

                # Validation du mot de passe (minimum 6 caractères)
                if len(user_data['password'].strip()) < 6:
                    self.console.print("[red]Le mot de passe doit contenir au moins 6 caractères[/red]")
                    continue

                user = User.create(**user_data)
                self.console.print(f"[green]Collaborateur {user.name} créé ![green]")
                return
            except Exception as e:
                self.console.print(f"[red]Erreur : {e}[red]")
                sentry_sdk.set_context("user_creation", {
                    "current_user_id": self.current_user.id if self.current_user else None,
                    "action": "create_error",
                    "user_data": user_data if 'user_data' in locals() else None,
                    "validation_error": missing_fields if 'missing_fields' in locals() else None
                })
                sentry_sdk.capture_exception(e)
                return

    def update_user(self):
        """Modifier un collaborateur"""
        session = None
        user_id = None

        try:
            self.list_users()
            user_id = self.user_view.get_user_id()
            session = db_manager.get_session()

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
            if session:
                session.rollback()
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[/red]")
            sentry_sdk.set_context("user_update", {
                "user_id": user_id,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "update_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()

    def delete_user(self):
        """Supprimer un collaborateur"""
        session = None
        user_id = None

        try:
            self.list_users()

            user_id = self.user_view.get_user_id()
            session = db_manager.get_session()

            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                self.console.print(f"[red]Collaborateur avec l'ID {user_id} introuvable.[/red]")
                return

            session.delete(user)
            session.commit()
            self.console.print(f"[green]Collaborateur {user.name} supprimé ![green]")
        except Exception as e:
            if session:
                session.rollback()
            self.console.print(f"[red]Erreur : {e}[red]")
            sentry_sdk.set_context("user_deletion", {
                "user_id": user_id,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "delete_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()

    def list_users(self, filter_by_department=None):
        """Lister tous les collaborateurs"""
        session = None

        try:
            session = db_manager.get_session()

            if filter_by_department:
                users = session.query(User).join(User.department).filter(
                    Department.name == filter_by_department
                ).all()
            else:
                users = session.query(User).all()

            # Forcer le chargement AVANT de fermer la session
            for user in users:
                _ = user.department.name if user.department else None

            self.user_view.display_user_list(users)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.set_context("user_listing", {
                "filter_by_department": filter_by_department,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "list_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()
