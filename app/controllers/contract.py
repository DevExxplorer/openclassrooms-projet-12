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
        session = None
        contract_data = None
        try:
            contract_data = self.contract_view.get_contract_creation_form()

            # Logique pour récupérer le commercial
            session = db_manager.get_session()

            client = session.query(Client).filter(Client.id == contract_data['client_id']).first()

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
        finally:
            if session:
                session.close()

    def update_contract(self, role):
        """Modifier un contrat"""
        session = None
        contract_id = None
        try:
            self.list_contracts(role=role)

            contract_id = self.contract_view.get_contract_id()
            session = db_manager.get_session()

            if role == "commercial":
                # Commercial : ne peut modifier que ses propres contrats
                contract = session.query(Contract).join(Contract.client).filter(
                    Contract.id == contract_id,
                    Client.commercial_contact_id == self.current_user.id
                ).first()

                if not contract:
                    self.console.print(f"[red]Contrat avec l'ID {contract_id} introuvable.[/red]")
                    return
            elif role == "gestion":
                # Gestion : peut modifier tous les contrats
                contract = session.query(Contract).filter(Contract.id == contract_id).first()
                if not contract:
                    self.console.print(f"[red]Contrat avec l'ID {contract_id} introuvable.[/red]")
                    return
            else:
                # Support : ne peut pas modifier les contrats
                self.console.print("[red]Vous n'êtes pas autorisé à modifier les contrats.[/red]")
                return

            updated_data = self.contract_view.get_contract_update_form(contract)

            for key, value in updated_data.items():
                if hasattr(contract, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(contract, key, value)

            session.commit()
            self.console.print(f"[green]Contrat {contract.id} mis à jour ![/green]")

        except Exception as e:
            if session:
                session.rollback()
            self.console.print(f"[red]Erreur : {e}[/red]")

            sentry_sdk.set_context("contract_update", {
                "contract_id": contract_id,
                "current_user_id": self.current_user.id if self.current_user else None,
                "role": role,
                "action": "update_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()

    def list_contracts(self, role):
        """Lister tous les contrats"""
        session = None
        try:
            session = db_manager.get_session()

            if role in ["gestion", "support"]:
                contracts = session.query(Contract).all()
            else:
                contracts = session.query(Contract).filter(
                    Contract.commercial_contact_id == self.current_user.id
                ).all()

            return self.contract_view.display_contract_list(contracts)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")

            sentry_sdk.set_context("contract_listing", {
                "role": role,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "list_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
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

    def filter_contracts(self, filter_type):
        """Filtrer les contrats selon différents critères"""
        session = None
        try:
            session = db_manager.get_session()

            base_query = session.query(Contract).filter(
                Contract.commercial_contact_id == self.current_user.id
            )

            if filter_type == "unsigned":
                contracts = base_query.filter(~Contract.is_signed).all()
            elif filter_type == "signed":
                contracts = base_query.filter(Contract.is_signed).all()
            elif filter_type == "unpaid":
                contracts = base_query.filter(Contract.remaining_amount > 0).all()

            self.contract_view.display_contract_list(contracts)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")

            sentry_sdk.set_context("contract_filtering", {
                "filter_type": filter_type,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "filter_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()
