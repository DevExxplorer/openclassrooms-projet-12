from app.commands import UserCommands, ContractCommands, ClientCommands, EventCommands
from rich.console import Console


class CommandRouter:
    def __init__(self, current_user=None):
        self.current_user = current_user
        self.user_cmd = UserCommands(current_user=current_user)
        self.contract_cmd = ContractCommands(current_user=current_user)
        self.client_cmd = ClientCommands(current_user=current_user)
        self.event_cmd = EventCommands(current_user=current_user)
        self.console = Console()

    def route_user_command(self, role, choice):
        """Route les commandes liées aux utilisateurs"""
        if role == "gestion":
            commands = {
                "1": lambda: self.user_cmd.create_user(),
                "2": lambda: self.user_cmd.update_user(),
                "3": lambda: self.user_cmd.delete_user(),
                "4": lambda: self.user_cmd.list_users(),
            }
        return commands.get(choice)

    def route_contract_command(self, role, choice):
        """Route les commandes liées aux contrats"""
        if role == "gestion":
            commands = {
                "1": lambda: self.contract_cmd.create_contract(),
                "2": lambda: self.contract_cmd.update_contract(),
                "3": lambda: self.contract_cmd.list_contracts(role),
            }
        elif role == "commercial":
            commands = {
                "1": lambda: self.contract_cmd.list_contracts(role),
                "2": lambda: self.contract_cmd.update_contract(),
                "3": lambda: self.contract_cmd.search_contract(),
            }
        return commands.get(choice)

    def route_client_command(self, role, choice):
        """Route les commandes liées aux clients"""
        if role == "commercial":
            commands = {
                "1": self.client_cmd.list_clients,
                "2": self.client_cmd.update_client,
                "3": self.client_cmd.research_client,
            }
        return commands.get(choice)

    def route_filters_command(self, role, choice):
        """Route les commandes liées aux filtres contrats"""
        if role == "commercial":
            commands = {
                "1": self.contract_cmd.filter_unsigned_contracts,
                "2": self.contract_cmd.filter_unpaid_contracts,
                "3": self.contract_cmd.filter_contracts_by_date,
                "4": self.contract_cmd.filter_contracts_by_amount,
            }
        return commands.get(choice)

    def route_event_command(self, role, choice):
        """Route les commandes liées aux événements"""
        if role == "gestion":
            commands = {
                "1": lambda: self.event_cmd.update_event(),
                "2": lambda: self.event_cmd.assign_support(),
                "3": lambda: self.event_cmd.list_events(role),
                "4": lambda: self.event_cmd.list_events(role, filter_no_support=True),
            }
        return commands.get(choice)

    def execute(self, command_type, role, choice):
        if command_type == "users":
            command = self.route_user_command(role, choice)
        elif command_type == "contracts":
            command = self.route_contract_command(role, choice)
        elif command_type == "events":
            command = self.route_event_command(role, choice)
        elif command_type == "clients":
            command = self.route_client_command(role, choice)
        elif command_type == "filters":
            command = self.route_filters_command(role, choice)
        else:
            command = None

        if command:
            command()
