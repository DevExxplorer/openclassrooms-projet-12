from app.models import Client
from app.views.client import ClientView
from rich.console import Console
from app.database.db import db_manager
import sentry_sdk


class ClientCommands:
    """Commandes liées aux clients"""
    def __init__(self, current_user=None, role=None):
        """Initialisation"""
        self.console = Console()
        self.view = ClientView()
        self.current_user = current_user
        self.role = role

    def create_client(self):
        """Créer un nouveau client"""
        try:
            client_data = self.view.get_client_creation_form()

            """Assigner le commercial courant comme contact principal"""
            client_data['commercial_contact_id'] = self.current_user.id

            client = Client.create('commercial', **client_data)
            self.console.print(f"[green]Client {client.name} créé ![green]")

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[red]")
            sentry_sdk.set_context("client_creation", {
                "commercial_id": self.current_user.id,
                "action": "create_error",
                "client_data": client_data if 'client_data' in locals() else None
            })
            sentry_sdk.capture_exception(e)

    def update_client(self):
        """Mettre à jour un client existant"""
        client_id = None
        try:
            client_id = self.view.get_id_client()

            # Rechercher le client dans la base de données
            client = Client.get_by_id_with_permissions(client_id, self.current_user.id)
            if not client:
                self.console.print(f"[red]Client avec l'ID {client_id} introuvable ou pas autorisé.[/red]")
                return

            # Obtenir les nouvelles données du client
            updated_data = self.view.get_client_update_form(client)

            # Mettre à jour les attributs du client
            client.update(**updated_data)
            self.console.print(f"[green]Client {client.name} mis à jour ![green]")
        except Exception as e:
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[red]")
            sentry_sdk.capture_exception(e)

    def list_clients(self, role="gestion"):
        """Lister tous les clients"""
        try:
            if role in ["gestion", "support"]:
                clients = Client.get_all()
            else:
                clients = Client.get_by_commercial(self.current_user.id)

            self.view.display_clients(clients)
        except Exception as e:
            self.console.print(f"[red]Erreur lors de l'affichage des clients : {e}[red]")
            sentry_sdk.capture_exception(e)

    def research_client(self):
        """Rechercher un client par nom"""
        try:
            # Obtenir le nom du client à rechercher
            name = self.view.research_client()

            # Rechercher les clients dans la base de données
            clients = Client.search_by_name(name)
            self.view.display_clients(clients)

        except Exception as e:
            self.console.print(f"[red]Erreur lors de la recherche : {e}[red]")
            sentry_sdk.capture_exception(e)
