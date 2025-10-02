from app.models import Client
from app.views.client import ClientView
from rich.console import Console
from app.database.db import db_manager


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
        client_data = self.view.get_client_creation_form()

        """Assigner le commercial courant comme contact principal"""
        client_data['commercial_contact_id'] = self.current_user.id

        try:
            client = Client.create('commercial', **client_data)
            self.console.print(f"[green]Client {client.name} créé ![green]")
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[red]")

    def list_clients(self):
        """Lister tous les clients"""
        session = db_manager.get_session()

        if self.role == "gestion":
            clients = session.query(Client).all()
        else:
            clients = session.query(Client).filter(
                Client.commercial_contact_id == self.current_user.id
            ).all()

        self.view.display_clients(clients)

    def update_client(self):
        """Mettre à jour un client existant"""
        # Obtenir une session de base de données
        session = db_manager.get_session()

        # Obtenir l'ID du client à mettre à jour
        client_id = self.view.get_id_client()

        # Rechercher le client dans la base de données
        client = session.query(Client).filter(Client.id == client_id).first()

        # Vérifier si le client existe
        if not client:
            self.console.print(f"[red]Client avec l'ID {client_id} introuvable.[/red]")
            return

        # Obtenir les nouvelles données du client
        updated_data = self.view.get_client_update_form(client)

        # Mettre à jour les attributs du client
        for key, value in updated_data.items():
            if hasattr(client, key) and value.strip():
                setattr(client, key, value)

        # Enregistrer les modifications dans la base de données
        try:
            session.commit()
            self.console.print(f"[green]Client {client.name} mis à jour ![green]")
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[red]")

    def research_client(self):
        """Rechercher un client par nom"""

        # Obtenir une session de base de données
        session = db_manager.get_session()

        # Obtenir le nom du client à rechercher
        name = self.view.research_client()

        # Rechercher les clients dans la base de données
        clients = session.query(Client).filter(Client.name.ilike(f"%{name}%")).all()

        self.view.display_clients(clients)
