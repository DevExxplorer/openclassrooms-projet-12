from app.commands.gestion import userCommands, ContractCommands
from app.commands.commercial import ClientCommands


class CommandRouter:
    def __init__(self, current_user=None):
        self.current_user = current_user
        self.user_cmd = userCommands(current_user=current_user)
        self.contract_cmd = ContractCommands(current_user=current_user)
        self.client_cmd = ClientCommands(current_user=current_user)

    def route_user_command(self, choice):
        """Route les commandes liées aux utilisateurs"""
        commands = {
            "1": self.user_cmd.create_user,
            "2": self.user_cmd.update_user,
            "3": self.user_cmd.delete_user,
            "4": self.user_cmd.list_users,
        }
        return commands.get(choice)

    def route_contract_command(self, choice):
        """Route les commandes liées aux contrats"""
        commands = {
            "1": self.contract_cmd.create_contract,
            "2": self.contract_cmd.update_contract,
            "4": self.contract_cmd.list_contracts,
            "5": self.contract_cmd.search_contract
        }
        return commands.get(choice)

    def route_client_command(self, choice):
        """Route les commandes liées aux clients"""
        commands = {
            "1": self.client_cmd.list_clients,
            "2": self.client_cmd.update_client,
            "3": self.client_cmd.research_client,
        }
        return commands.get(choice)

    def execute(self, command_type, choice):
        if command_type == "users":
            command = self.route_user_command(choice)
        elif command_type == "contracts":
            command = self.route_contract_command(choice)
        elif command_type == "clients":
            command = self.route_client_command(choice)
        else:
            command = None

        if command:
            command()
        else:
            print("[red]Choix invalide[/red]")
