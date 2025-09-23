from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table


class UserView:
    """Vue pour les opérations liées aux utilisateurs"""
    def __init__(self):
        self.console = Console()

    def get_user_creation_form(self):
        """Affiche le formulaire de création d'utilisateur et retourne les données"""
        self.console.print("[bold blue]Création d'un nouveau collaborateur[/bold blue]\n")
        name = Prompt.ask("Nom complet")
        mail = Prompt.ask("Email")
        username = Prompt.ask("Nom d'utilisateur")
        password = Prompt.ask("Mot de passe", password=True)
        department = Prompt.ask("Département", choices=["commercial", "support", "gestion"])

        return {
            'name': name,
            'mail': mail,
            'username': username,
            'password': password,
            'department': department
        }

    def get_employee_number(self):
        """Demande le numéro d'employé pour les opérations de mise à jour ou de suppression"""
        employee_number = Prompt.ask("Entrez le numéro d'employé du collaborateur")
        return employee_number

    def get_user_update_form(self, user):
        """Affiche le formulaire de mise à jour d'utilisateur et retourne les données"""
        self.console.print(f"[blue]Mise à jour du collaborateur {user.name} (Numéro: {user.employee_number})[/blue]\n")
        name = Prompt.ask("Nom complet", default=user.name)
        mail = Prompt.ask("Email", default=user.mail)
        username = Prompt.ask("Nom d'utilisateur", default=user.username)
        department = Prompt.ask("Département", choices=["commercial", "support", "gestion"], default=user.department.name)

        return {
            'name': name,
            'mail': mail,
            'username': username,
            'department': department
        }

    def display_user_list(self, users):
        """Affiche une liste d'utilisateurs dans un tableau"""
        if not users:
            self.console.print("[yellow]Aucun collaborateur trouvé.[/yellow]")
            return

        # Créer le tableau
        table = Table(title="[bold blue]Liste des collaborateurs[/bold blue]")

        # Ajouter les colonnes
        table.add_column("Numéro", style="cyan", no_wrap=True)
        table.add_column("Nom", style="magenta")
        table.add_column("Email", style="green")
        table.add_column("Département", style="yellow")
        table.add_column("Créé le", style="dim")

        # Ajouter les lignes
        for user in users:
            dept_name = user.department.name if user.department else "N/A"
            created_date = user.created_at.strftime('%d/%m/%Y') if user.created_at else "N/A"

            table.add_row(
                user.employee_number,
                user.name,
                user.mail,
                dept_name,
                created_date
            )

        # Afficher le tableau
        self.console.print("\n" * 2)
        self.console.print(table)
        self.console.print("\n" * 2)
