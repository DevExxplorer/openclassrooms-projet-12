from app.commands.gestion import UserCommands, ContractCommands

class CommandRouter:
    def __init__(self):
        self.user_cmd = UserCommands()
        self.contract_cmd = ContractCommands()

    def route_user_command(self, choice):
        """Route les commandes liées aux utilisateurs"""
        commands = {
            "1": self.user_cmd.create_user,
            "2": self.user_cmd.update_user,
            "3": self.user_cmd.delete_user,
            "4": self.user_cmd.list_users
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

    def execute(self, command_type, choice):
        if command_type == "users":
            command = self.route_user_command(choice)
        elif command_type == "contracts":
            command = self.route_contract_command(choice)
        
        if command:
            command()
        else:
            print("[red]Choix invalide[/red]")
