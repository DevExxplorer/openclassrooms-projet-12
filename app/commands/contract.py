from app.views.contract import ContractView
from app.models.contract import Contract
from rich.console import Console
from app.database.db import db_manager


class ContractCommands:
    def __init__(self, current_user=None):
        self.contract_view = ContractView()
        self.console = Console()
        self.current_user = current_user

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

            if contract.commercial_contact_id != self.current_user.id:
                self.console.print(f"[red]Vous n'avez pas de contrat avec l'ID {contract_id}.[/red]")
                return

            updated_data = self.contract_view.get_contract_update_form(contract)

            for key, value in updated_data.items():
                if hasattr(contract, key) and value and str(value).strip():
                    setattr(contract, key, value)

            session.commit()
            self.console.print(f"[green]Contrat {contract.id} mis à jour ![/green]")

        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()

    def list_contracts(self, role):
        """Lister tous les contrats"""
        session = db_manager.get_session()
        try:
            if role == "gestion":
                contracts = session.query(Contract).all()
            else:
                contracts = session.query(Contract).filter(
                    Contract.commercial_contact_id == self.current_user.id
                ).all()

            return self.contract_view.display_contract_list(contracts)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()

    def search_contract(self):
        """Rechercher un contrat"""
        contract_id = self.contract_view.research_contract()
        session = db_manager.get_session()
        try:
            contract = session.query(Contract).filter(Contract.id == contract_id).first()
            if not contract:
                self.console.print(f"[red]Contrat avec l'ID {contract_id} introuvable.[/red]")
                return
            self.contract_view.display_contract_list([contract])
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()

    def filter_unsigned_contracts(self):
        """Filtrer les contrats non signés"""
        self.filter_contracts("unsigned")

    def filter_signed_contracts(self):
        """Filtrer les contrats signés"""
        self.filter_contracts("signed") 

    def filter_unpaid_contracts(self):
        """Filtrer les contrats avec montant restant"""
        self.filter_contracts("unpaid")

    def filter_contracts_by_date(self):
        """Filtrer les contrats par date de création"""
        self.filter_contracts("by_date")

    def filter_contracts_by_amount(self):
        """Filtrer les contrats par montant total"""
        self.filter_contracts("by_amount")

    def filter_contracts(self, filter_type):
        """Filtrer les contrats selon différents critères"""
        session = db_manager.get_session()
        try:
            base_query = session.query(Contract).filter(
                Contract.commercial_contact_id == self.current_user.id
            )

            if filter_type == "unsigned":
                contracts = base_query.filter(~Contract.is_signed).all()
            elif filter_type == "signed":
                contracts = base_query.filter(Contract.is_signed).all()
            elif filter_type == "unpaid":
                contracts = base_query.filter(Contract.remaining_amount > 0).all()
            elif filter_type == "by_date":
                date_filter = self.contract_view.get_date_filter()
                contracts = base_query.filter(Contract.created_at >= date_filter).all()
            elif filter_type == "by_amount":
                amount_filter = self.contract_view.get_amount_filter()
                contracts = base_query.filter(Contract.total_amount >= amount_filter).all()

            self.contract_view.display_contract_list(contracts)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()
