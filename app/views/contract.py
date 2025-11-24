from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from app.controllers.client import ClientCommands
from app.controllers.user import UserCommands
from datetime import datetime


class ContractView:
    """Vue liées aux contrats"""
    def __init__(self):
        self.console = Console()

    def get_contract_creation_form(self):
        """Affiche le formulaire de création de contrat et retourne les données"""

        self.console.print("[blue]Création d'un nouveau contrat[/blue]\n")

        # Afficher la liste des clients
        ClientCommands(role="gestion").list_clients()
        client_id = Prompt.ask("ID du client")

        total_amount = Prompt.ask("Montant total", default=0.00)
        remaining_amount = Prompt.ask("Montant restant à payer", default=0.00)
        status = Prompt.ask("Statut", choices=["signé", "non signé"], default="non signé")

        return {
            'client_id': client_id,
            'total_amount': total_amount,
            'remaining_amount': remaining_amount,
            'status': status
        }

    def get_contract_id(self):
        """Obtenir l'ID du contrat à mettre à jour"""
        try:
            contract_id = self.console.input("Entrez l'ID du contrat à mettre à jour : ")
            return int(contract_id.strip())
        except ValueError:
            self.console.print("[red]ID invalide. Veuillez entrer un nombre.[/red]")
            return None

    def get_contract_update_form(self, contract):
        """Formulaire de mise à jour d'un contrat existant"""
        self.console.print(f"[blue]Mise à jour du contrat : {contract.id}[/blue]")

        # Obtenir les nouvelles données du contrat
        total_amount = Prompt.ask("Montant total", default=str(contract.total_amount))
        remaining_amount = Prompt.ask("Montant restant à payer", default=str(contract.remaining_amount or "0"))
        current_status = "signé" if contract.is_signed else "non signé"
        status = Prompt.ask("Statut", choices=["signé", "non signé"], default=current_status)

        return {
            'total_amount': float(total_amount),
            'remaining_amount': float(remaining_amount),
            'is_signed': status == "signé"
        }

    def display_contract_list(self, contracts):
        """Afficher la liste des contrats"""
        if not contracts:
            self.console.print("[yellow]Aucun contrat trouvé.[/yellow]")
            return

        table = Table(title="[bold blue]Liste des contrats[/bold blue]")

        # Ajouter les colonnes
        table.add_column("ID Contrat", style="cyan", no_wrap=True)
        table.add_column("Client", style="magenta")  # Nom du client
        table.add_column("Commercial", style="blue")  # Nom du commercial
        table.add_column("Montant total", style="green")
        table.add_column("Montant restant", style="yellow")
        table.add_column("Statut")
        table.add_column("Créé le", style="dim")
        table.add_column("Modifier le", style="dim")

        # Ajouter les lignes
        for contract in contracts:
            if contract.is_signed:
                status_formatted = "[green]Signé[/green]"
            else:
                status_formatted = "[red]Non signé[/red]"

            table.add_row(
                str(contract.id),
                contract.client.name,
                contract.commercial_contact.name,
                f"{contract.total_amount}€",
                f"{contract.remaining_amount}€",
                status_formatted,
                contract.created_at.strftime("%d-%m-%Y"),
                contract.last_updated_at.strftime("%d-%m-%Y")
            )

        self.console.print("\n" * 2)
        self.console.print(table)
        self.console.print("\n" * 2)

    def research_contract(self):
        """Rechercher un contrat par ID"""
        search_term = self.console.input("Entrez l'ID du contrat à rechercher : ")
        return search_term.strip()

    def get_date_filter(self):
        """Obtenir une date pour filtrer les contrats"""
        date_str = self.console.input("Entrez la date minimale (DD-MM-YYYY) : ")
        try:
            date_obj = datetime.strptime(date_str.strip(), "%d-%m-%Y")
            return date_obj  # Retourne un objet datetime, pas une string
        except ValueError:
            self.console.print("[red]Format de date invalide. Utilisez DD-MM-YYYY[/red]")
            return None

    def get_amount_filter(self):
        """Obtenir un montant pour filtrer les contrats"""
        try:
            amount_str = self.console.input("Entrez le montant minimal : ")
            return float(amount_str.strip())
        except ValueError:
            self.console.print("[red]Montant invalide. Veuillez entrer un nombre.[/red]")
            return None

    def get_commercial_id(self):
        """Demande l'ID du commercial"""
        UserCommands().list_users(filter_by_department="commercial")
        return Prompt.ask("ID du commercial responsable")
