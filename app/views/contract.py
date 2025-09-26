from rich.console import Console
from rich.prompt import Prompt


class ContractView:
    """Vue liées aux contrats"""
    def __init__(self):
        self.console = Console()

    def get_contract_creation_form(self):
        """Affiche le formulaire de création de contrat et retourne les données"""

        self.console.print("[bold blue]Création d'un nouveau contrat[/bold blue]\n")

        client_id = Prompt.ask("ID du client")
        commercial_contact_id = Prompt.ask("ID du commercial responsable")
        total_amount = Prompt.ask("Montant total")
        remaining_amount = Prompt.ask("Montant restant à payer")
        status = Prompt.ask("Statut", choices=["signé", "non signé"], default="non signé")

        return {
            'client_id': client_id,
            'commercial_contact_id': commercial_contact_id,
            'total_amount': total_amount,
            'remaining_amount': remaining_amount,
            'status': status
        }

    def get_contract_id(self):
        pass

    def get_contract_update_form(self, contract):
        pass

    def display_contract_list(self, contracts):
        pass

    def display_contract(self, contract):
        pass
