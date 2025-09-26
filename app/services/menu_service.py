from rich.console import Console
from app.models import Department
from app.views.menu import Menu, Submenu
from app.utils.constants import MESSAGES, MENU_MAPPING
from app.services.command_router import CommandRouter


class MenuService:
    def __init__(self):
        self.console = Console()
        self.router = None

    def handle_main_menu(self, user):
        """Gère l'affichage et la sélection des options dans le menu principal"""

        # Initialisation du routeur de commandes avec l'utilisateur courant
        self.router = CommandRouter(current_user=user)

        # Récupération du département
        dept_name = self._get_user_department(user)

        # Affichage du menu principal
        menu = Menu(dept_name)
        menu.display()

        while True:
            choice = menu.get_choice()
            if menu.is_valid_choice(choice):
                if choice == "0":
                    return "logout"

                submenu_key = MENU_MAPPING[dept_name.lower()].get(choice)

                if not submenu_key:
                    # Si pas de sous-menu, gérer les actions directes
                    if dept_name.lower() == "commercial":
                        if choice == "2":
                            return "create_client"

                    self.console.print("[red]Sous-menu non trouvé[/red]")
                    continue

                result = self.handle_submenu(submenu_key)

                if result == "back_to_main":
                    break

                return result

            self.console.print(MESSAGES["invalid_option"])

    def handle_submenu(self, submenu_key):
        """Gère l'affichage et la sélection des options dans un sous-menu"""

        if submenu_key:
            submenu = Submenu(submenu_key)
            submenu.display()

            while True:
                choice = submenu.get_choice()
                if submenu.is_valid_choice(choice):
                    if choice == "0":  # Retour au menu principal
                        return "back_to_main"

                    self._route_to_command(submenu_key, choice)
                    break
                self.console.print(MESSAGES["invalid_option"])

    def _get_user_department(self, user):
        """Méthode récupérer le département"""
        try:
            dept_name = Department.get_department_with_id(user.department_id)
            if not dept_name:
                self.console.print(MESSAGES["invalid_department"])
                return None
            return dept_name
        except Exception as e:
            self.console.print(f"[red]Erreur: {e}[/red]")
            return None

    def _route_to_command(self, submenu_key, choice):
        """Méthode pour diriger vers les bonnes commandes"""
        if submenu_key == "gestion_collaborateurs":
            self.router.execute("users", choice)
        elif submenu_key == "gestion_contrats":
            self.router.execute("contracts", choice)
        elif submenu_key == "gestion_evenements":
            self.router.execute("events", choice)
        elif submenu_key == "commercial_mes_clients":
            self.router.execute("clients", choice)
        else:
            self.console.print(f"[red]Sous-menu '{submenu_key}' non implémenté[/red]")
