import click
import getpass
from rich.console import Console

from app.models.user import User
from app.services.initialization import Initialization

console = Console()

def show_menu():
    """Menu principal de l'application"""
    console.print("[cyan]=====Bienvenue dans l'outil EPIC Events=====[/cyan]\n")
    console.print("Veuillez vous connecter pour accéder à l'application.\n")

    username = input("Nom d'utilisateur : ")
    password = getpass.getpass("Mot de passe : ")

    user = User.authenticate(username, password)
    if user:
        console.print(f"[green]Connexion réussie ! Bienvenue {user.name}[/green]")
    else:
        console.print("[red]Nom d'utilisateur ou mot de passe incorrect[/red]")

def initialize_database():
    """Initialiser la base de données avec les données de base"""
    console.print("[yellow]Initialisation de la base de données...[/yellow]\n")

    results = Initialization.initialize_application()

    if results['errors']:
        console.print("[red]Erreurs rencontrées :[/red]")
        for error in results['errors']:
            console.print(f"  - {error}")
        return False

    console.print(f"\n[green]✓ Initialisation terminée avec succès ![/green]")
    return True

@click.command()
@click.option('--dev-init', is_flag=True, hidden=True, help="[DEV] Initialiser la base de données")
@click.option('--command', '-c', help="Commande à exécuter")
def cli(dev_init, command):
    if dev_init:
        initialize_database()
    elif command == "login":
        console.print("Login executé")
    else:
        show_menu()

if __name__ == "__main__":
    cli()
