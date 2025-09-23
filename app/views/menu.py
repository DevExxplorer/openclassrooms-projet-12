from rich.console import Console
from rich.table import Table
from app.utils.constants import MENU, SUBMENUS


class MenuManager:
    def __init__(self):
        self.console = Console()
        self.items = []

    def display(self):
        """Affiche le menu"""
        table = Table()
        table.add_column("Option", style="cyan", width=8)
        table.add_column("Description", style="white")

        for item in self.items:
            table.add_row(item["option"], item["title"])

        self.console.print(table)

    def get_choice(self):
        """Récupère le choix de l'utilisateur"""
        return self.console.input("\n[bold yellow]Choisissez une option: [/bold yellow]")

    def is_valid_choice(self, choice):
        """Vérifie si le choix est valide"""
        return any(item["option"] == choice for item in self.items)


class Menu(MenuManager):
    """Classe pour les menus principaux"""

    def __init__(self, department):
        super().__init__()
        self.department = department
        self.items = MENU[department]


class Submenu(MenuManager):
    """Classe pour les sous-menus"""

    def __init__(self, submenu_key):
        super().__init__()
        self.submenu_key = submenu_key
        self.items = SUBMENUS[submenu_key]
