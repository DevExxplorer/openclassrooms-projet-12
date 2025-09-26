from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt


class ClientView:
    def __init__(self):
        self.console = Console()

    def get_client_creation_form(self):
        """Formulaire de création d'un nouveau client"""
        self.console.print("[blue]Création d'un nouveau client[/blue]")
        name = self.console.input("Nom du client : ")
        mail = self.console.input("Email du client : ")
        phone = self.console.input("Téléphone du client : ")
        company_name = self.console.input("Entreprise du client : ")

        return {
            "name": name,
            "mail": mail,
            "phone": phone,
            "company_name": company_name,
        }

    def display_clients(self, clients):
        """Afficher une liste de clients"""
        if not clients:
            self.console.print("[yellow]Aucun client trouvé.[/yellow]")
            return

        table = Table(title="[bold blue]Liste des clients[/bold blue]")

        # Ajouter les colonnes
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Nom", style="cyan", no_wrap=True)
        table.add_column("Email", style="magenta")
        table.add_column("Téléphone", style="green")
        table.add_column("Entreprise", style="yellow")
        table.add_column("Créé le", style="dim")
        table.add_column("Modifier le", style="dim")

        # Ajouter les lignes
        for client in clients:
            table.add_row(
                str(client.id),
                client.name,
                client.mail,
                client.phone,
                client.company_name,
                client.created_at.strftime("%Y-%m-%d"),
                client.last_updated_at.strftime("%Y-%m-%d")
            )

        self.console.print("\n" * 2)
        self.console.print(table)
        self.console.print("\n" * 2)

    def get_id_client(self):
        """Obtenir l'ID du client à mettre à jour"""
        client_id = self.console.input("Entrez l'ID du client à mettre à jour : ")
        return client_id.strip()

    def get_client_update_form(self, client):
        """Formulaire de mise à jour d'un client existant"""
        self.console.print(f"[blue]Mise à jour du client : {client.name}[/blue]")
        name = Prompt.ask("Nom du client", default=client.name or "")
        mail = Prompt.ask("Email du client", default=client.mail or "")
        phone = Prompt.ask("Téléphone du client", default=client.phone or "")
        company_name = Prompt.ask("Entreprise du client", default=client.company_name or "")

        return {
            "name": name,
            "mail": mail,
            "phone": phone,
            "company_name": company_name,
        }

    def research_client(self):
        """Rechercher un client par nom"""
        search_term = self.console.input("Entrez le nom du client à rechercher : ")
        return search_term.strip()
