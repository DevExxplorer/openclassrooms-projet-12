from rich.console import Console
from app.commands import ContractCommands
from app.views.event import EventView
from app.models.event import Event
from app.models.user import User
from app.database.db import db_manager
from app.models.department import Department


class EventCommands:
    def __init__(self, current_user):
        self.current_user = current_user
        self.console = Console()
        self.event_view = EventView(contract_id=None)

    def create_event(self):
        self.console.print("[yellow]Création d'un nouvel événement...[/yellow]")

        # Tableau des contrats signés
        ContractCommands(self.current_user).filter_signed_contracts()

        # Choix du contrat
        choice_contract = self.console.input("Entrez l'ID du contrat : ")
        self.console.print(f"[green]Vous avez choisi le contrat ID {choice_contract}[/green]")

        # Formulaire de création d'événement
        event_data = EventView(choice_contract).get_event_creation_form()

        try:
            event = Event.create(**event_data)
            self.console.print(f"[green]Événement {event.id} créé ![/green]")
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")

    def update_event(self):
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

        # Rechercher l'événement dans la base de données
        try:
            event_id = int(choice_event)
        except ValueError:
            self.console.print("[red]ID invalide. Veuillez entrer un nombre.[/red]")
            return

        event = session.query(Event).filter(Event.id == event_id).first()
        if not event:
            self.console.print(f"[red]Événement avec l'ID {event_id} introuvable.[/red]")
            return

        # Formulaire de mise à jour d'événement
        updated_event_data = EventView(choice_event).get_event_update_form(event)

        # Mettre à jour les attributs de l'événement
        for key, value in updated_event_data.items():
            if hasattr(event, key) and value is not None:
                if isinstance(value, str) and not value.strip():
                    continue
                setattr(event, key, value)

        # Enregistrer les modifications dans la base de données
        try:
            session.commit()
            self.console.print(f"[green]Événement {event.id} mis à jour ![/green]")
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur lors de la mise à jour : {e}[red]")

    def list_events(self, role=None, filter_no_support=False):
        """Lister les événements"""
        session = db_manager.get_session()
        try:
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
        finally:
            session.close()

    def assign_support(self):
        self.console.print("[yellow]Assigner un support à un événement...[/yellow]")

        # Liste des événements sans support
        self.filter_events_without_support()

        # Choix de l'événement
        session = db_manager.get_session()
        choice_event = self.console.input("Entrez l'ID de l'événement à assigner : ")

        # Rechercher l'événement dans la base de données
        event = session.query(Event).filter(Event.id == choice_event).first()

        # Vérifier si l'événement existe
        if not event:
            self.console.print(f"[red]Événement avec l'ID {choice_event} introuvable.[/red]")
            return

        # Liste des supports disponibles
        supports = session.query(User).join(User.department).filter(
            Department.name == 'support'
        ).all()

        if not supports:
            self.console.print("[red]Aucun support disponible.[/red]")
            return

        self.console.print("Supports disponibles :")
        self.event_view.display_supports_available(supports)

        # Choix du support
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
        try:
            session.commit()
            self.console.print(f"[green]Support {support.name} assigné à l'événement {event.id} ![/green]")
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Erreur lors de l'assignation : {e}[red]")
        finally:
            session.close()

    def filter_events_without_support(self):
        """Filtrer les événements sans support assigné"""
        session = db_manager.get_session()
        try:
            events = session.query(Event).filter(Event.support_contact_id.is_(None)).all()
            if not events:
                self.console.print("[green]Tous les événements ont un support assigné.[/green]")
                return

            return self.event_view.display_event_list(events)
        except Exception as e:
            self.console.print(f"[red]Erreur : {e}[/red]")
        finally:
            session.close()
