import getpass
import json
import jwt
from datetime import datetime, timedelta, timezone
from pathlib import Path
from rich.console import Console
from app.models.user import User
import sentry_sdk
import os


class AuthService:
    def __init__(self, console=None):
        self.console = console or Console()
        self.secret_key = os.getenv('SECRET_KEY')
        self.token_file = Path.home() / '.epic_token'

    def authenticate_user(self):
        try:
            # Vérifier s'il y a déjà un token valide
            existing_user = self._check_existing_token()
            if existing_user:
                return existing_user

            # Sinon, connexion normale
            self.console.print("Veuillez vous connecter pour accéder à l'application.\n")
            username = input("Nom d'utilisateur : ")
            password = getpass.getpass("Mot de passe : ")

            user = User.authenticate(username, password)
            if user:  # Vérification que user n'est pas None
                self._save_token(user)
                return user
            else:
                self.console.print("[red]Nom d'utilisateur ou mot de passe incorrect[/red]")
                return None

        except Exception as e:
            sentry_sdk.set_context("auth_service_authenticate", {
                "action": "authenticate_error",
                "username": username if 'username' in locals() else None,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e

    def _check_existing_token(self):
        """Vérifie si un token valide existe et retourne l'objet User"""
        try:
            if self.token_file.exists():
                with open(self.token_file, 'r') as f:
                    data = json.load(f)

                payload = jwt.decode(data['token'], self.secret_key, algorithms=['HS256'])
                self.console.print("[green]Déjà connecté ![/green]")

                # Récupérer l'objet User depuis la base
                user = User.get_by_id(payload['user_id'])
                return user

        except Exception as e:
            print(f"Erreur token: {e}")
            if self.token_file.exists():
                self.token_file.unlink()

            sentry_sdk.set_context("auth_service_check_token", {
                "action": "check_token_error",
                "token_file_exists": self.token_file.exists() if self.token_file else None,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)

        return None

    def _save_token(self, user):
        """Sauvegarde un token JWT"""
        try:
            if not user:
                raise ValueError("User object is None")

            if not hasattr(user, 'id') or not hasattr(user, 'username'):
                raise ValueError(f"User object missing required attributes: {user}")

            payload = {
                'user_id': user.id,
                'username': user.username,
                'exp': datetime.now(timezone.utc) + timedelta(hours=24)
            }
            token = jwt.encode(payload, self.secret_key, algorithm='HS256')

            with open(self.token_file, 'w') as f:
                json.dump({'token': token}, f)

            self.console.print("[green]Connexion sauvegardée ![/green]")

        except Exception as e:
            sentry_sdk.set_context("auth_service_save_token", {
                "action": "save_token_error",
                "user_id": user.id if user else None,
                "username": user.username if user else None,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e

    def logout(self):
        """Supprime le token (déconnexion)"""
        try:
            if self.token_file.exists():
                self.token_file.unlink()
                self.console.print("[green]Déconnexion réussie[/green]")
                return True
            return False

        except Exception as e:
            sentry_sdk.set_context("auth_service_logout", {
                "action": "logout_error",
                "token_file_exists": self.token_file.exists() if self.token_file else None,
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            raise e
