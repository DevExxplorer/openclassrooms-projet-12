from app.views.user import userView
from app.models.user import User
from rich.console import Console
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
        user_id = None
        try:
            self.list_users()
            user_id = self.user_view.get_user_id()

            user = User.get_by_id(user_id)
            if not user:
                self.console.print(f"[red]Collaborateur avec l'ID {user_id} introuvable.[/red]")
                return

            updated_data = self.user_view.get_user_update_form(user)
            user.update(**updated_data)
            self.console.print(f"[green]Collaborateur {user.name} mis à jour avec succès ![/green]")

        except Exception as e:
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[/red]")
            sentry_sdk.capture_exception(e)

    def delete_user(self):
        """Supprimer un collaborateur"""
        user_id = None
        try:
            self.list_users()
            user_id = self.user_view.get_user_id()

            user = User.get_by_id(user_id)
            if not user:
                self.console.print(f"[red]Collaborateur avec l'ID {user_id} introuvable.[/red]")
                return

            User.delete(user.id, 'gestion')  # Rôle gestion pour les permissions
            self.console.print(f"[green]Collaborateur {user.name} supprimé ![green]")
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[red]")
            sentry_sdk.capture_exception(e)

    def list_users(self, filter_by_department=None):
        """Lister tous les collaborateurs"""
        try:
            if filter_by_department:
                users = User.get_by_department(filter_by_department)
            else:
                users = User.get_all()

            self.user_view.display_user_list(users)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.capture_exception(e)
