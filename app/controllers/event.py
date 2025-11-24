from rich.console import Console
from app.controllers import ContractCommands
from app.views.event import EventView
from app.models.event import Event
from app.models.user import User
from app.database.db import db_manager
from app.models.department import Department
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
        session = None
        choice_contract = None
        event_data = None

        try:
            self.console.print("[yellow]Création d'un nouvel événement...[/yellow]")

            # Tableau des contrats signés
            ContractCommands(self.current_user).filter_signed_contracts()

            # Choix du contrat
            choice_contract = self.console.input("Entrez l'ID du contrat : ")

            session = db_manager.get_session()

            # Vérifier que le contrat existe et est signé et appartient au commercial
            contract = session.query(Contract).join(Contract.client).filter(
                Contract.id == choice_contract,
                Contract.is_signed,
                Client.commercial_contact_id == self.current_user.id
            ).first()

            if not contract:
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

            # Capturer l'exception avec Sentry
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()

    def update_event(self):
        """Mettre à jour un événement existant"""
        session = None
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

            # Choix de l'événement
            session = db_manager.get_session()

            choice_event = self.console.input("Entrez l'ID de l'événement à modifier : ")

            # Validation de l'ID
            try:
                event_id = int(choice_event)
            except ValueError:
                self.console.print("[red]ID invalide. Veuillez entrer un nombre.[/red]")
                return

            # Récupérer l'événement en fonction du rôle de l'utilisateur
            if user_role == "support":
                # Support : seulement ses événements assignés
                event = session.query(Event).filter(
                    Event.id == event_id,
                    Event.support_contact_id == self.current_user.id
                ).first()

            if not event:
                self.console.print(f"[red]Événement {event_id} introuvable ou vous n'y êtes pas assigné.[/red]")
                return

            elif user_role == "gestion":
                # Gestion : tous les événements
                event = session.query(Event).filter(Event.id == event_id).first()

                if not event:
                    self.console.print(f"[red]Événement avec l'ID {event_id} introuvable.[/red]")
                    return

            else:
                # Commercial : pas autorisé à modifier les événements
                self.console.print("[red]Vous n'êtes pas autorisé à modifier les événements.[/red]")
                return

            updated_event_data = EventView(choice_event).get_event_update_form(event)

            if not updated_event_data:
                return

            for key, value in updated_event_data.items():
                if hasattr(event, key) and value is not None:
                    if isinstance(value, str) and not value.strip():
                        continue
                    setattr(event, key, value)

            session.commit()
            self.console.print(f"[green]Événement {event.id} mis à jour ![/green]")

        except Exception as e:
            if session:
                session.rollback()
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[/red]")

            sentry_sdk.set_context("event_update", {
                "event_id": event_id,
                "current_user_id": self.current_user.id if self.current_user else None,
                "user_role": user_role,
                "action": "update_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()

    def list_events(self, role=None, filter_no_support=False):
        """Lister les événements"""
        session = None

        try:
            session = db_manager.get_session()

            if role == "gestion":
                events = session.query(Event).all()
            elif role == "support":
                events = session.query(Event).filter(
                    Event.support_contact_id == self.current_user.id
                ).all()

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
        finally:
            if session:
                session.close()

    def assign_support(self):
        """Assigner un support à un événement sans support"""
        session = None
        choice_event = None
        choice_support = None

        try:
            self.console.print("[yellow]Assigner un support à un événement...[/yellow]")

            session = db_manager.get_session()

            # Vérifier s'il y a des événements sans support
            events_without_support = session.query(Event).filter(Event.support_contact_id.is_(None)).all()

            if not events_without_support:
                self.console.print("[yellow]Aucun événement sans support trouvé.[/yellow]")
                return

            # Afficher les événements sans support
            self.filter_events_without_support()

            choice_event = self.console.input("Entrez l'ID de l'événement à assigner : ")

            # Rechercher l'événement dans la base de données
            event = session.query(Event).filter(Event.id == choice_event).first()

            # Vérifier si l'événement existe
            if not event:
                self.console.print(f"[red]Événement avec l'ID {choice_event} introuvable.[/red]")
                return

            # Vérifier les supports disponibles
            supports = session.query(User).join(User.department).filter(
                Department.name == 'support'
            ).all()

            if not supports:
                self.console.print("[red]Aucun support disponible.[/red]")
                return

            self.console.print("Supports disponibles :")
            self.event_view.display_supports_available(supports)

            # Id du support à assigner
            choice_support = self.console.input("Entrez l'ID du support à assigner : ")

            # Rechercher le support dans la base de données
            support = session.query(User).join(User.department).filter(
                User.id == choice_support,
                Department.name == 'support'
            ).first()

            # Vérifier si le support existe
            if not support:
                self.console.print(f"[red]Support avec l'ID {choice_support} introuvable ou n'est pas un support.[/red]")
                return

            # Assigner le support à l'événement
            event.support_contact_id = support.id

            # Enregistrer les modifications dans la base de données
            session.commit()
            self.console.print(f"[green]Support {support.name} assigné à l'événement {event.id} ![/green]")

        except Exception as e:
            if session:
                session.rollback()
            self.console.print(f"[red]Erreur lors de l'assignation : {e}[/red]")

            sentry_sdk.set_context("event_support_assignment", {
                "event_id": choice_event,
                "support_id": choice_support,
                "current_user_id": self.current_user.id if self.current_user else None,
                "action": "assign_support_error"
            })
            sentry_sdk.capture_exception(e)
        finally:
            if session:
                session.close()

    def filter_events_without_support(self):
        """Filtrer les événements sans support assigné"""
        session = None

        try:
            session = db_manager.get_session()

            events = session.query(Event).filter(Event.support_contact_id.is_(None)).all()
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
        finally:
            if session:
                session.close()
