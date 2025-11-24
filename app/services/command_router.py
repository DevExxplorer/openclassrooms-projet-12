from app.controllers import UserCommands, ContractCommands, ClientCommands, EventCommands
from rich.console import Console
import sentry_sdk


class CommandRouter:
    def __init__(self, current_user=None):
        self.current_user = current_user
        self.user_cmd = UserCommands(current_user=current_user)
        self.contract_cmd = ContractCommands(current_user=current_user)
        self.client_cmd = ClientCommands(current_user=current_user)
        self.event_cmd = EventCommands(current_user=current_user)
        self.console = Console()

        self.command_map = {
            # Users - Gestion
            ("users", "gestion", "1"): lambda: self.user_cmd.create_user(),
            ("users", "gestion", "2"): lambda: self.user_cmd.update_user(),
            ("users", "gestion", "3"): lambda: self.user_cmd.delete_user(),
            ("users", "gestion", "4"): lambda: self.user_cmd.list_users(),

            # Contracts - Gestion
            ("contracts", "gestion", "1"): lambda: self.contract_cmd.create_contract(),
            ("contracts", "gestion", "2"): lambda: self.contract_cmd.update_contract("gestion"),
            ("contracts", "gestion", "3"): lambda: self.contract_cmd.list_contracts("gestion"),

            # Contracts - Commercial
            ("contracts", "commercial", "1"): lambda: self.contract_cmd.list_contracts("commercial"),
            ("contracts", "commercial", "2"): lambda: self.contract_cmd.update_contract("commercial"),

            # Clients - Commercial
            ("clients", "commercial", "1"): lambda: self.client_cmd.list_clients(),
            ("clients", "commercial", "2"): lambda: self.client_cmd.update_client(),

            # Filters - Commercial
            ("filters", "commercial", "1"): lambda: self.contract_cmd.filter_unsigned_contracts(),
            ("filters", "commercial", "2"): lambda: self.contract_cmd.filter_unpaid_contracts(),

            # Events - Gestion
            ("events", "gestion", "1"): lambda: self.event_cmd.update_event(),
            ("events", "gestion", "2"): lambda: self.event_cmd.assign_support(),
            ("events", "gestion", "3"): lambda: self.event_cmd.list_events("gestion"),
            ("events", "gestion", "4"): lambda: self.event_cmd.list_events("gestion", filter_no_support=True),

            # Actions directes
            ("direct", "create_client", ""): lambda: self.client_cmd.create_client(),
            ("direct", "create_event", ""): lambda: self.event_cmd.create_event(),
            ("direct", "list_all_clients", ""): lambda: self.client_cmd.list_clients("support"),
            ("direct", "list_assigned_events", ""): lambda: self.event_cmd.list_events("support"),
            ("direct", "update_event", ""): lambda: self.event_cmd.update_event(),
            ("direct", "list_all_contracts", ""): lambda: self.contract_cmd.list_contracts("support")
        }

    def execute(self, command_type, role, choice):
        """Exécute la commande en fonction du type, rôle et choix"""
        try:
            command = self.command_map.get((command_type, role, choice))

            if command:
                command()
            else:
                self.console.print(f"[red]Commande non trouvée: {command_type}/{role}/{choice}[/red]")

        except Exception as e:
            self.console.print(f"[red]Erreur lors de l'exécution de la commande: {e}[/red]")

            sentry_sdk.set_context("command_router_execute", {
                "command_type": command_type,
                "role": role,
                "choice": choice,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "execute_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)

    def execute_direct_action(self, action):
        """Exécute les actions directes"""
        try:
            command = self.command_map.get(("direct", action, ""))
            if command:
                command()
            else:
                self.console.print(f"[red]Action directe non trouvée: {action}[/red]")

        except Exception as e:
            self.console.print(f"[red]Erreur lors de l'exécution de l'action: {e}[/red]")

            sentry_sdk.set_context("command_router_direct", {
                "action": action,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action_type": "execute_direct_error",
                "error_type": type(e).__name__
            })
            sentry_sdk.capture_exception(e)
