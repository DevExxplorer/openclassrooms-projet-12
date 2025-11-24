from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from datetime import datetime


class EventView:
    """Vue liées aux événements"""
    def __init__(self, contract_id):
        self.console = Console()
        self.contract_id = contract_id

    def get_event_creation_form(self):
        """Affiche le formulaire de création d'événement et retourne les données"""

        self.console.print("[bold blue]Création d'un nouvel événement[/bold blue]\n")

        event_name = Prompt.ask("Nom de l'événement ")

        while True:
            date_start_input = Prompt.ask("Date/heure de début (DD-MM-YYYY HH:MM)")

            try:
                date_start = datetime.strptime(date_start_input, "%d-%m-%Y %H:%M")

                # Vérifier que la date de début n'est pas dans le passé
                if date_start <= datetime.now():
                    self.console.print("[red]❌ La date de début ne peut pas être dans le passé ![/red]")
                    continue
                break
            except ValueError:
                self.console.print("[red]Format de date invalide ! Utilisez DD-MM-YYYY HH:MM[/red]")

        while True:
            date_end_input = Prompt.ask("Date/heure de fin (DD-MM-YYYY HH:MM)")

            try:
                date_end = datetime.strptime(date_end_input, "%d-%m-%Y %H:%M")

                # Vérifier que la date de début n'est pas dans le passé
                if date_end <= datetime.now():
                    self.console.print("[red]❌ La date de fin ne peut pas être dans le passé ![/red]")
                    continue

                # Vérifier que la date de fin est après la date de début
                if date_end <= date_start:
                    self.console.print("[red]❌ La date de fin doit être après la date de début ![/red]")
                    continue
                break
            except ValueError:
                self.console.print("[red]Format de date invalide ! Utilisez DD-MM-YYYY HH:MM[/red]")

        event_location = Prompt.ask("Localisation de l'événement ")
        event_attendees = Prompt.ask("Nombre de participants ")
        event_notes = Prompt.ask("Notes supplémentaires ")

        return {
            'contract_id': self.contract_id,
            'name': event_name,
            'date_start': date_start,
            'date_end': date_end,
            'location': event_location,
            'attendees': event_attendees,
            'notes': event_notes
        }

    def display_event_list(self, events):
        """Affiche une liste d'événements"""
        if not events:
            self.console.print("[red]Aucun événement trouvé.[/red]")
            return

        table = Table(title="Liste des événements")

        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Nom", style="magenta")
        table.add_column("Contrat ID", justify="right", style="green")
        table.add_column("Début", style="yellow")
        table.add_column("Fin", style="yellow")
        table.add_column("Localisation", style="white")
        table.add_column("Participants", justify="right", style="blue")
        table.add_column("Notes", style="white")
        table.add_column("Support", style="red")

        for event in events:
            # Récupération du nom du support
            support_name = f"[green]{event.support_contact.name}[/green]" if event.support_contact else "[red]NON ASSIGNÉ[/red]"

            table.add_row(
                str(event.id),
                event.name,
                str(event.contract_id),
                event.date_start.strftime("%d-%m-%Y %H:%M"),
                event.date_end.strftime("%d-%m-%Y %H:%M"),
                event.location,
                str(event.attendees),
                event.notes or "",
                support_name
            )

        self.console.print(table)

    def get_event_update_form(self, event):
        """Affiche le formulaire de mise à jour d'événement et retourne les données"""

        self.console.print("[blue]Mise à jour d'un événement[/blue]\n")

        event_name = Prompt.ask("Nom de l'événement: ", default=event.name)
        date_start_input = Prompt.ask(
            "Date/heure de début (DD-MM-YYYY HH:MM)",
            default=event.date_start.strftime("%d-%m-%Y %H:%M")
        )
        date_end_input = Prompt.ask(
            "Date/heure de fin (DD-MM-YYYY HH:MM)",
            default=event.date_end.strftime("%d-%m-%Y %H:%M")
        )
        event_location = Prompt.ask("Localisation de l'événement", default=event.location)
        event_attendees = Prompt.ask("Nombre de participants", default=event.attendees)
        event_notes = Prompt.ask("Notes supplémentaires", default=event.notes)

        # Validation des dates
        date_start = self._parse_date(date_start_input, "début")
        date_end = self._parse_date(date_end_input, "fin")

        if date_start_input and not date_start:
            return None
        if date_end_input and not date_end:
            return None

        event_data = {
            'name': event_name,
            'date_start': date_start,
            'date_end': date_end,
            'location': event_location,
            'attendees': event_attendees,
            'notes': event_notes
        }
        filtered_data = {}
        for field_name, field_value in event_data.items():
            if field_value:
                filtered_data[field_name] = field_value

        return filtered_data

    def display_supports_available(self, supports):
        """Affiche une liste des supports disponibles"""
        if not supports:
            self.console.print("[red]Aucun support trouvé.[/red]")
            return

        table = Table(title="Liste des supports")

        table.add_column("ID", justify="right", style="cyan", no_wrap=True)
        table.add_column("Nom", style="magenta")

        for support in supports:
            table.add_row(
                str(support.id),
                support.name
            )

        self.console.print(table)

    def _parse_date(self, date_input, field_name="date"):
        """Méthode privée pour parser les dates"""
        if not date_input:
            return None
        try:
            return datetime.strptime(date_input, "%d-%m-%Y %H:%M")
        except ValueError:
            self.console.print(f"[red]Format de date invalide pour {field_name} ! Utilisez DD-MM-YYYY HH:MM[/red]")
            return None
