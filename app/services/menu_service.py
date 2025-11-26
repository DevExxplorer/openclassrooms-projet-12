from rich.console import Console
from app.models import Department
from app.views.menu import Menu, Submenu
from app.utils.constants import MESSAGES, MENU_MAPPING
from app.services.command_router import CommandRouter
from app.utils.constants import DIRECT_ACTIONS
import sentry_sdk


class MenuService:
    def __init__(self):
        self.console = Console()
        self.router = None

    def handle_main_menu(self, user):
        """Gère l'affichage et la sélection des options dans le menu principal"""

        try:
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
                    # Retour et déconnexion
                    if choice == "0":
                        return "logout"

                    # Récupération de la clé du sous-menu
                    submenu_key = MENU_MAPPING[dept_name.lower()].get(choice)

                    # Si action directe
                    if not submenu_key:
                        action = DIRECT_ACTIONS.get((dept_name.lower(), choice))

                        if action:
                            self.router.execute_direct_action(action)
                        else:
                            self.console.print("[red]Action non trouvée[/red]")
                            continue

                    result = self.handle_submenu(submenu_key)

                    # Retour au menu principal depuis le sous-menu
                    if result == "back_to_main":
                        break

                    return result

                self.console.print(MESSAGES["invalid_option"])
        except Exception as e:
            self.console.print(f"[red]Erreur dans le menu principal: {e}[/red]")

            sentry_sdk.set_context("menu_service_main", {
                "user_id": user.id if user else None,
                "department_name": dept_name if 'dept_name' in locals() else None,
                "action": "handle_main_menu_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)

    def handle_submenu(self, submenu_key):
        """Gère l'affichage et la sélection des options dans un sous-menu"""
        try:
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

        except Exception as e:
            self.console.print(f"[red]Erreur dans le sous-menu: {e}[/red]")

            sentry_sdk.set_context("menu_service_submenu", {
                "submenu_key": submenu_key,
                "action": "handle_submenu_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)

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

            sentry_sdk.set_context("menu_service_department", {
                "user_id": user.id if user else None,
                "user_department_id": user.department_id if user else None,
                "action": "get_department_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
            return None

    def _route_to_command(self, submenu_key, choice):
        """Méthode pour diriger vers les bonnes commandes"""

        try:
            routing_map = {
                "gestion_collaborateurs": ("users", "gestion"),
                "gestion_contrats": ("contracts", "gestion"),
                "gestion_evenements": ("events", "gestion"),
                "commercial_mes_clients": ("clients", "commercial"),
                "commercial_mes_contrats": ("contracts", "commercial"),
                "commercial_filtres_contrats": ("filters", "commercial"),
                "support_modifier_evenements": ("events", "support"),
            }

            if submenu_key in routing_map:
                command_type, role = routing_map[submenu_key]
                self.router.execute(command_type, role, choice)
            else:
                self.console.print(f"[red]Sous-menu '{submenu_key}' non implémenté[/red]")

        except Exception as e:
            self.console.print(f"[red]Erreur lors du routage: {e}[/red]")

            sentry_sdk.set_context("menu_service_routing", {
                "submenu_key": submenu_key,
                "choice": choice,
                "action": "route_to_command_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
