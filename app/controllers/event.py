from rich.console import Console
from app.controllers import ContractCommands
from app.views.event import EventView
from app.models.event import Event
from app.database.db import db_manager
from app.models.contract import Contract
from app.models.client import Client
import sentry_sdk


class EventCommands:
    def __init__(self, current_user):
        self.current_user = current_user
        self.console = Console()
        self.event_view = EventView(contract_id=None)

    def create_event(self):
        """Créer un nouvel événement"""
        choice_contract = None
        event_data = None

        try:
            self.console.print("[yellow]Création d'un nouvel événement...[/yellow]")

            # Tableau des contrats signés
            ContractCommands(self.current_user).filter_signed_contracts()

            # Choix du contrat
            choice_contract = self.console.input("Entrez l'ID du contrat : ")

            # Vérifier que le contrat existe et est signé et appartient au commercial
            if not Event.validate_contract_access(choice_contract, self.current_user.id):
                self.console.print(f"[red]Contrat {choice_contract} introuvable, non signé, ou vous n'y êtes pas autorisé.[/red]")
                return

            self.console.print(f"[green]Vous avez choisi le contrat ID {choice_contract}[/green]")

            event_data = EventView(choice_contract).get_event_creation_form()

            if event_data:
                event = Event.create(**event_data)
                self.console.print(f"[green]Événement {event.id} créé ![/green]")

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.set_context("event_creation", {
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "create_error",
                "contract_id": choice_contract,
                "event_data": event_data if event_data else None
            })
            sentry_sdk.capture_exception(e)

    def update_event(self):
        """Mettre à jour un événement existant"""
        event_id = None
        user_role = None

        try:
            self.console.print("[yellow]Mise à jour d'un événement...[/yellow]")

            try:
                user_role = self.current_user.department.name
            except AttributeError:
                user_role = "gestion"

            # Liste des événements
            self.list_events(role=user_role)

            choice_event = self.console.input("Entrez l'ID de l'événement à modifier : ")

            # Validation de l'ID
            try:
                event_id = int(choice_event)
            except ValueError:
                self.console.print("[red]ID invalide. Veuillez entrer un nombre.[/red]")
                return

            # Vérifier les permissions via le modèle
            if user_role not in ["support", "gestion"]:
                self.console.print("[red]Vous n'êtes pas autorisé à modifier les événements.[/red]")
                return

            # Récupérer l'événement avec permissions
            event = Event.get_event_with_permissions(event_id, self.current_user.id, user_role)
            if not event:
                self.console.print(f"[red]Événement {event_id} introuvable ou vous n'y êtes pas assigné.[/red]")
                return

            updated_event_data = EventView(choice_event).get_event_update_form(event)

            if not updated_event_data:
                return

            event.update(**updated_event_data)
            self.console.print(f"[green]Événement {event.id} mis à jour ![/green]")

        except Exception as e:
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[/red]")
            sentry_sdk.set_context("event_update", {
                "event_id": event_id,
                "current_user_id": self.current_user.id if self.current_user else None,
                "user_role": user_role,
                "action": "update_error"
            })
            sentry_sdk.capture_exception(e)


    def list_events(self, role=None, filter_no_support=False):
        """Lister les événements"""
        try:
            if role == "gestion":
                events = Event.get_all()
            elif role == "support":
                events = Event.get_by_support_user(self.current_user.id)
            else:
                events = Event.get_all()

            if filter_no_support:
                events = [event for event in events if not event.support_contact]

            return self.event_view.display_event_list(events)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.set_context("event_listing", {
                "role": role,
                "filter_no_support": filter_no_support,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "list_error"
            })
            sentry_sdk.capture_exception(e)

    def assign_support(self):
        """Assigner un support à un événement sans support"""
        try:
            self.console.print("[yellow]Assigner un support à un événement...[/yellow]")

            # Vérifier s'il y a des événements sans support
            events_without_support = Event.get_events_without_support()

            if not events_without_support:
                self.console.print("[yellow]Aucun événement sans support trouvé.[/yellow]")
                return

            # Afficher les événements sans support
            self.filter_events_without_support()

            choice_event = self.console.input("Entrez l'ID de l'événement à assigner : ")

            # Récupérer l'événement
            try:
                event = Event.get_by_id(choice_event)
            except ValueError as e:
                self.console.print(f"[red]Événement avec l'ID {choice_event} introuvable.[/red]")
                return

            # Récupérer et afficher les supports disponibles
            supports = Event.get_available_supports()
            if not supports:
                self.console.print("[red]Aucun support disponible.[/red]")
                return

            self.console.print("Supports disponibles :")
            self.event_view.display_supports_available(supports)

            choice_support = self.console.input("Entrez l'ID du support à assigner : ")

            # Valider le support
            support = Event.validate_support_user(choice_support)
            if not support:
                self.console.print(f"[red]Support avec l'ID {choice_support} introuvable ou n'est pas un support.[/red]")
                return

            # Assigner le support
            event.assign_support(support.id)
            self.console.print(f"[green]Support {support.name} assigné à l'événement {event.id} ![/green]")

        except Exception as e:
            self.console.print(f"[red]Erreur lors de l'assignation : {e}[/red]")
            sentry_sdk.set_context("event_support_assignment", {
                "event_id": choice_event,
                "support_id": choice_support,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "assign_support_error"
            })
            sentry_sdk.capture_exception(e)

    def filter_events_without_support(self):
        """Filtrer les événements sans support assigné"""
        try:
            events = Event.get_events_without_support()

            if not events:
                self.console.print("[green]Tous les événements ont un support assigné.[/green]")
                return

            return self.event_view.display_event_list(events)

        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
            sentry_sdk.set_context("event_filter_no_support", {
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "filter_no_support_error"
            })
            sentry_sdk.capture_exception(e)
