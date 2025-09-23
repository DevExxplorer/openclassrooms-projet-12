from rich.console import Console
from app.models import Department
from app.views.menu import Menu, Submenu
from app.utils.constants import MESSAGES, MENU_MAPPING
from app.commands.gestion_commands import GestionCommands


class MenuService:
    def __init__(self):
        self.console = Console()


    def handle_main_menu(self, user):
        """Gère l'affichage du menu principal"""
        # Récupération du département
        dept_name = self._get_user_department(user)
        if not dept_name:
            return "logout"

        # Affichage du menu principal
        menu = Menu(dept_name)
        menu.display()
        
        while True:
            choice = menu.get_choice()
            if menu.is_valid_choice(choice):
                if choice == "0":
                    return "logout"
                
                submenu_key = MENU_MAPPING[dept_name.lower()].get(choice)
                result = self.handle_submenu(submenu_key)
                if result == "back_to_main":
                    continue
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
        else:
            self.console.print("[yellow]Action directe - pas de sous-menu[/yellow]")


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
            gestion_cmd = GestionCommands()
            if choice == "1":
                gestion_cmd.create_user()
            elif choice == "2":
                gestion_cmd.update_user()
            elif choice == "3":
                gestion_cmd.delete_user()
            elif choice == "4":
                gestion_cmd.list_users()
        elif submenu_key == "gestion_contrats":
            pass
        