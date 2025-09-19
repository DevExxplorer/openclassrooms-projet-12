import click
import getpass
from rich.console import Console

from app.models import Department
from app.models.user import User
from app.services.initialization import Initialization
from app.utils.constants import MESSAGES, MENU_MAPPING, SUBMENUS
from app.views.menu import Menu, Submenu

console = Console()

def main_loop():
    """Boucle principale de l'application"""
    while True:
        result = show_menu()

def show_menu():
    """Menu principal de l'application"""
    console.print(MESSAGES["welcome"])

    # Authentification
    user = authenticate_user()
    if not user:
        console.print(MESSAGES["invalid_user"])
        return
    console.print(f"[green]Connexion réussie ! Bienvenue {user.name}[/green]\n")

    # Récupération du département de l'utilisateur
    dept_name = get_user_department(user)
    if not dept_name:
        return

    while True:
        result = handle_main_menu(user, dept_name)
        if result == "logout":
            return
        elif result == "back_to_main":
            continue

def authenticate_user():
    """Gère l'authentification"""
    console.print("Veuillez vous connecter pour accéder à l'application.\n")
    username = input("Nom d'utilisateur : ")
    password = getpass.getpass("Mot de passe : ")
    return User.authenticate(username, password)

def handle_main_menu(user, dept_name):
    """Gère l'affichage du menu principal"""
    menu = Menu(dept_name)
    menu.display()
    
    while True:
        choice = menu.get_choice()

        if menu.is_valid_choice(choice):
            if choice == "0":
                return "logout"
            
            submenu_key = MENU_MAPPING[dept_name.lower()].get(choice)
            return handle_submenu(submenu_key)
            break

        console.print(MESSAGES["invalid_option"])

def handle_submenu(submenu_key):
    """Gère l'affichage et la sélection des options dans un sous-menu"""
    
    if submenu_key:
        submenu = Submenu(submenu_key)
        submenu.display()

        while True:
            choice = submenu.get_choice()
            if submenu.is_valid_choice(choice):
                if choice == "0":  # Retour au menu principal
                    return "back_to_main"

                console.print("[yellow]Action directe - pas de sous-menu[/yellow]")
                break
            console.print(MESSAGES["invalid_option"])
    else:
        console.print("[yellow]Action directe - pas de sous-menu[/yellow]")

def get_user_department(user):
    """Récupère et valide le département d'un utilisateur"""
    try:
        dept_name = Department.get_department_with_id(user.department_id)
        if not dept_name:
            console.print(MESSAGES["invalid_department"])
            return None
        return dept_name
    except Exception as e:
        console.print(f"[red]Erreur: {e}[/red]")
        return None
    
def initialize_database():
    """
    Initialiser la base de données avec les données de base
    Peux être effectué en ajoutant le parametre --dev-init
    """
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
def user_cli(dev_init, command):
    """Redirige vers la bonne view en fonction du type de l'utilisateur"""
    if dev_init:
        initialize_database()
    elif command == "login":
        console.print("Login executé")
    else:
        main_loop()