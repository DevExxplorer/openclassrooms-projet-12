import click
from rich.console import Console

from app.services.auth_service import AuthService
from app.services.menu_service import MenuService
from app.services.initialization import Initialization
from app.utils.constants import MESSAGES

console = Console()


def main_loop():
    """Boucle principale de l'application"""
    while True:
        result = show_menu()
        if result == "exit":
            break


def show_menu():
    """Menu principal de l'application"""
    console.print(MESSAGES["welcome"])

    # Authentification
    auth_service = AuthService()
    user = auth_service.authenticate_user()
    if not user:
        console.print(MESSAGES["invalid_user"])
        return "continue"

    console.print(f"[green]Connexion réussie ! Bienvenue {user.name}[/green]\n")

    # Navigation dans les menus
    menu_service = MenuService()
    while True:
        result = menu_service.handle_main_menu(user)
        if result == "logout":
            return "continue"
        elif result == "exit":
            return "exit"


def initialize_database():
    """
    Initialiser la base de données avec les données de base
    Peut être effectué en ajoutant le paramètre --dev-init
    """
    console.print("[yellow]Initialisation de la base de données...[/yellow]\n")

    results = Initialization.initialize_application()

    if results['errors']:
        console.print("[red]Erreurs rencontrées :[/red]")
        for error in results['errors']:
            console.print(f"  - {error}")
        return False

    console.print("\n[green]✓ Initialisation terminée avec succès ![/green]")
    return True


@click.command()
@click.option('--dev-init', is_flag=True, hidden=True, help="[DEV] Initialiser la base de données")
@click.option('--command', '-c', help="Commande à exécuter")
def main_cli(dev_init, command):
    """Interface en ligne de commande pour Epic Events CRM"""
    if dev_init:
        initialize_database()
    elif command == "login":
        console.print("Login executé")
    else:
        main_loop()
