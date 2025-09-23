import getpass
from rich.console import Console
from app.models.user import User


class AuthService:
    def __init__(self, console=None):
        self.console = console or Console()

    def authenticate_user(self):
        """Gère l'authentification"""
        self.console.print("Veuillez vous connecter pour accéder à l'application.\n")
        username = input("Nom d'utilisateur : ")
        password = getpass.getpass("Mot de passe : ")
        return User.authenticate(username, password)
