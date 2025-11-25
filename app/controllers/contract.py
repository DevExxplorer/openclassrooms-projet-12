from app.views.contract import ContractView
from app.models.contract import Contract
from app.models.client import Client
from rich.console import Console
from app.database.db import db_manager
import sentry_sdk


class ContractCommands:
    def __init__(self, current_user=None):
        self.contract_view = ContractView()
        self.console = Console()
        self.current_user = current_user

    def create_contract(self):
        """Créer un contrat"""
        contract_data = None
        try:
            contract_data = self.contract_view.get_contract_creation_form()

            if not contract_data:
                return
            
            client = Contract.get_client_with_commercial(contract_data['client_id'])

            if not client:
                self.console.print("[red]Client introuvable[/red]")
                return

            if client.commercial_contact_id:
                contract_data['commercial_contact_id'] = client.commercial_contact_id
                self.console.print(
                    f"[green]Commercial assigné: {client.commercial_contact.name}[/green]"
                )
            else:
                contract_data['commercial_contact_id'] = self.contract_view.get_commercial_id()

            contract = Contract.create(**contract_data)
            self.console.print(f"[green]Contrat {contract.id} créé ![/green]")

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.set_context("contract_creation", {
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "create_error",
                "contract_data": contract_data if contract_data else None,
                "client_id": contract_data.get('client_id') if contract_data else None
            })
            sentry_sdk.capture_exception(e)

    def update_contract(self, role):
        """Modifier un contrat"""
        contract_id = None
        try:
            self.list_contracts(role=role)
            contract_id = self.contract_view.get_contract_id()

            # Utiliser le modèle au lieu de session
            contract = Contract.get_by_id_with_permissions(contract_id, self.current_user.id, role)
            if not contract:
                self.console.print(f"[red]Contrat avec l'ID {contract_id} introuvable.[/red]")
                return

            updated_data = self.contract_view.get_contract_update_form(contract)
            
            # Utiliser la méthode update du modèle
            contract.update(**updated_data)
            self.console.print(f"[green]Contrat {contract.id} mis à jour ![/green]")

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.capture_exception(e)

    def list_contracts(self, role):
        """Lister tous les contrats"""
        try:
            # Utiliser le modèle
            if role in ["gestion", "support"]:
                contracts = Contract.get_all()
            else:
                contracts = Contract.get_by_commercial(self.current_user.id)

            return self.contract_view.display_contract_list(contracts)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.capture_exception(e)

    def filter_unsigned_contracts(self):
        """Filtrer les contrats non signés"""
        self.filter_contracts("unsigned")

    def filter_signed_contracts(self):
        """Filtrer les contrats signés"""
        self.filter_contracts("signed")

    def filter_unpaid_contracts(self):
        """Filtrer les contrats avec montant restant"""
        self.filter_contracts("unpaid")

    def filter_contracts(self, filter_type):
        """Filtrer les contrats selon différents critères"""
        try:
            contracts = Contract.get_filtered_contracts(self.current_user.id, filter_type)
            self.contract_view.display_contract_list(contracts)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.capture_exception(e)