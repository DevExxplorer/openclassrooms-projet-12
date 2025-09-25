from app.views.contract_view import ContractView
from app.models.contract import Contract
from rich.console import Console
from app.database.db import db_manager

class ContractCommands:
    def __init__(self):
        self.contract_view = ContractView()
        self.console = Console()

    def create_contract(self):
        """Créer un contrat"""
        contract_data = self.contract_view.get_contract_creation_form()
        try:
            contract = Contract.create(**contract_data)
            self.console.print(f"[green]Contrat {contract.id} créé ![/green]")
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")

    def update_contract(self):
        """Modifier un contrat"""
        contract_id = self.contract_view.get_contract_id()
        session = db_manager.get_session()

        try:
            contract = session.query(Contract).filter(Contract.id == contract_id).first()
            if not contract:
                self.console.print(f"[red]Contrat avec l'ID {contract_id} introuvable.[/red]")
                return

            updated_data = self.contract_view.get_contract_update_form(contract)

            for key, value in updated_data.items():
                if hasattr(contract, key) and value.strip():
                    setattr(contract, key, value)

            session.commit()
            self.console.print(f"[green]Contrat {contract.id} mis à jour ![/green]")

        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()

    def list_contracts(self):
        """Lister tous les contrats"""
        session = db_manager.get_session()
        try:
            contracts = session.query(Contract).all()
            self.contract_view.display_contract_list(contracts)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()

    def search_contract(self):
        """Rechercher un contrat"""
        contract_id = self.contract_view.get_contract_id()
        session = db_manager.get_session()
        try:
            contract = session.query(Contract).filter(Contract.id == contract_id).first()
            if not contract:
                self.console.print(f"[red]Contrat avec l'ID {contract_id} introuvable.[/red]")
                return
            self.contract_view.display_contract(contract)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()