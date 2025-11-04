import pytest
from unittest.mock import Mock, patch

from app.services.command_router import CommandRouter


class TestCommandRouter:
    """Tests pour CommandRouter"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.name = "Test User"

        # Mock tous les imports dans le constructeur
        with patch('app.services.command_router.UserCommands') as mock_user_cmd, \
            patch('app.services.command_router.ContractCommands') as mock_contract_cmd, \
            patch('app.services.command_router.ClientCommands') as mock_client_cmd, \
            patch('app.services.command_router.EventCommands') as mock_event_cmd:

            self.command_router = CommandRouter(current_user=self.mock_user)

            # Stocker les mocks pour les tests
            self.mock_user_cmd = self.command_router.user_cmd
            self.mock_contract_cmd = self.command_router.contract_cmd
            self.mock_client_cmd = self.command_router.client_cmd
            self.mock_event_cmd = self.command_router.event_cmd

            # Mock de la console
            self.command_router.console = Mock()

    def test_init_with_current_user(self):
        """Test initialisation avec current_user"""
        assert self.command_router.current_user == self.mock_user

    def test_init_without_current_user(self):
        """Test initialisation sans current_user"""
        with patch('app.services.command_router.UserCommands'), \
            patch('app.services.command_router.ContractCommands'), \
            patch('app.services.command_router.ClientCommands'), \
            patch('app.services.command_router.EventCommands'):

            router = CommandRouter()
            assert router.current_user is None

    # Tests pour les commandes Users - Gestion
    def test_execute_users_gestion_create(self):
        """Test création d'utilisateur"""
        self.command_router.execute("users", "gestion", "1")
        self.mock_user_cmd.create_user.assert_called_once()

    def test_execute_users_gestion_update(self):
        """Test mise à jour d'utilisateur"""
        self.command_router.execute("users", "gestion", "2")
        self.mock_user_cmd.update_user.assert_called_once()

    def test_execute_users_gestion_delete(self):
        """Test suppression d'utilisateur"""
        self.command_router.execute("users", "gestion", "3")
        self.mock_user_cmd.delete_user.assert_called_once()

    def test_execute_users_gestion_list(self):
        """Test listage d'utilisateurs"""
        self.command_router.execute("users", "gestion", "4")
        self.mock_user_cmd.list_users.assert_called_once()

    # Tests pour les commandes Contracts - Gestion
    def test_execute_contracts_gestion_create(self):
        """Test création de contrat"""
        self.command_router.execute("contracts", "gestion", "1")
        self.mock_contract_cmd.create_contract.assert_called_once()

    def test_execute_contracts_gestion_update(self):
        """Test mise à jour de contrat"""
        self.command_router.execute("contracts", "gestion", "2")
        self.mock_contract_cmd.update_contract.assert_called_once_with("gestion")

    def test_execute_contracts_gestion_list(self):
        """Test listage de contrats"""
        self.command_router.execute("contracts", "gestion", "3")
        self.mock_contract_cmd.list_contracts.assert_called_once_with("gestion")

    # Tests pour les commandes Contracts - Commercial
    def test_execute_contracts_commercial_list(self):
        """Test listage de contrats commercial"""
        self.command_router.execute("contracts", "commercial", "1")
        self.mock_contract_cmd.list_contracts.assert_called_once_with("commercial")

    def test_execute_contracts_commercial_update(self):
        """Test mise à jour de contrat commercial"""
        self.command_router.execute("contracts", "commercial", "2")
        self.mock_contract_cmd.update_contract.assert_called_once_with("commercial")

    # Tests pour les commandes Clients - Commercial
    def test_execute_clients_commercial_list(self):
        """Test listage de clients"""
        self.command_router.execute("clients", "commercial", "1")
        self.mock_client_cmd.list_clients.assert_called_once()

    def test_execute_clients_commercial_update(self):
        """Test mise à jour de client"""
        self.command_router.execute("clients", "commercial", "2")
        self.mock_client_cmd.update_client.assert_called_once()

    # Tests pour les filtres - Commercial
    def test_execute_filters_commercial_unsigned(self):
        """Test filtre contrats non signés"""
        self.command_router.execute("filters", "commercial", "1")
        self.mock_contract_cmd.filter_unsigned_contracts.assert_called_once()

    def test_execute_filters_commercial_unpaid(self):
        """Test filtre contrats impayés"""
        self.command_router.execute("filters", "commercial", "2")
        self.mock_contract_cmd.filter_unpaid_contracts.assert_called_once()

    # Tests pour les commandes Events - Gestion
    def test_execute_events_gestion_update(self):
        """Test mise à jour d'événement"""
        self.command_router.execute("events", "gestion", "1")
        self.mock_event_cmd.update_event.assert_called_once()

    def test_execute_events_gestion_assign_support(self):
        """Test assignation de support"""
        self.command_router.execute("events", "gestion", "2")
        self.mock_event_cmd.assign_support.assert_called_once()

    def test_execute_events_gestion_list(self):
        """Test listage d'événements"""
        self.command_router.execute("events", "gestion", "3")
        self.mock_event_cmd.list_events.assert_called_once_with("gestion")

    def test_execute_events_gestion_list_no_support(self):
        """Test listage d'événements sans support"""
        self.command_router.execute("events", "gestion", "4")
        self.mock_event_cmd.list_events.assert_called_once_with("gestion", filter_no_support=True)

    # Tests pour les actions directes
    def test_execute_direct_action_create_client(self):
        """Test action directe création client"""
        self.command_router.execute_direct_action("create_client")
        self.mock_client_cmd.create_client.assert_called_once()

    def test_execute_direct_action_create_event(self):
        """Test action directe création événement"""
        self.command_router.execute_direct_action("create_event")
        self.mock_event_cmd.create_event.assert_called_once()

    def test_execute_direct_action_list_all_clients(self):
        """Test action directe listage clients"""
        self.command_router.execute_direct_action("list_all_clients")
        self.mock_client_cmd.list_clients.assert_called_once_with("support")

    def test_execute_direct_action_list_assigned_events(self):
        """Test action directe listage événements assignés"""
        self.command_router.execute_direct_action("list_assigned_events")
        self.mock_event_cmd.list_events.assert_called_once_with("support")

    def test_execute_direct_action_update_event(self):
        """Test action directe mise à jour événement"""
        self.command_router.execute_direct_action("update_event")
        self.mock_event_cmd.update_event.assert_called_once()

    def test_execute_direct_action_list_all_contracts(self):
        """Test action directe listage contrats"""
        self.command_router.execute_direct_action("list_all_contracts")
        self.mock_contract_cmd.list_contracts.assert_called_once_with("support")

    # Tests pour les commandes non trouvées
    def test_execute_command_not_found(self):
        """Test commande non trouvée"""
        self.command_router.execute("invalid", "role", "choice")
        self.command_router.console.print.assert_called_once_with(
            "[red]Commande non trouvée: invalid/role/choice[/red]"
        )

    def test_execute_direct_action_not_found(self):
        """Test action directe non trouvée"""
        self.command_router.execute_direct_action("invalid_action")
        self.command_router.console.print.assert_called_once_with(
            "[red]Action directe non trouvée: invalid_action[/red]"
        )

    # Tests de toutes les clés du command_map pour s'assurer qu'elles existent
    def test_all_command_map_keys_exist(self):
        """Test que toutes les clés du command_map existent"""
        expected_keys = [
            # Users - Gestion
            ("users", "gestion", "1"),
            ("users", "gestion", "2"),
            ("users", "gestion", "3"),
            ("users", "gestion", "4"),
            # Contracts - Gestion
            ("contracts", "gestion", "1"),
            ("contracts", "gestion", "2"),
            ("contracts", "gestion", "3"),
            # Contracts - Commercial
            ("contracts", "commercial", "1"),
            ("contracts", "commercial", "2"),
            # Clients - Commercial
            ("clients", "commercial", "1"),
            ("clients", "commercial", "2"),
            # Filters - Commercial
            ("filters", "commercial", "1"),
            ("filters", "commercial", "2"),
            # Events - Gestion
            ("events", "gestion", "1"),
            ("events", "gestion", "2"),
            ("events", "gestion", "3"),
            ("events", "gestion", "4"),
            # Actions directes
            ("direct", "create_client", ""),
            ("direct", "create_event", ""),
            ("direct", "list_all_clients", ""),
            ("direct", "list_assigned_events", ""),
            ("direct", "update_event", ""),
            ("direct", "list_all_contracts", "")
        ]

        for key in expected_keys:
            assert key in self.command_router.command_map, f"Clé manquante: {key}"

    def test_command_map_functions_are_callable(self):
        """Test que toutes les fonctions du command_map sont appelables"""
        for key, func in self.command_router.command_map.items():
            assert callable(func), f"La fonction pour la clé {key} n'est pas appelable"

    # Tests pour vérifier que les commands sont bien initialisées avec current_user
    def test_commands_initialized_with_current_user(self):
        """Test que les commandes sont initialisées avec current_user"""
        with patch('app.services.command_router.UserCommands') as mock_user_cmd, \
            patch('app.services.command_router.ContractCommands') as mock_contract_cmd, \
            patch('app.services.command_router.ClientCommands') as mock_client_cmd, \
            patch('app.services.command_router.EventCommands') as mock_event_cmd:

            test_user = Mock()
            CommandRouter(current_user=test_user)

            # Vérifier que toutes les commandes sont initialisées avec current_user
            mock_user_cmd.assert_called_once_with(current_user=test_user)
            mock_contract_cmd.assert_called_once_with(current_user=test_user)
            mock_client_cmd.assert_called_once_with(current_user=test_user)
            mock_event_cmd.assert_called_once_with(current_user=test_user)

    # Test des cas edge
    def test_execute_with_empty_strings(self):
        """Test execute avec chaînes vides"""
        self.command_router.execute("", "", "")
        self.command_router.console.print.assert_called_once_with(
            "[red]Commande non trouvée: //[/red]"
        )

    def test_execute_direct_action_with_empty_string(self):
        """Test execute_direct_action avec chaîne vide"""
        self.command_router.execute_direct_action("")
        self.command_router.console.print.assert_called_once_with(
            "[red]Action directe non trouvée: [/red]"
        )

    def test_execute_with_none_values(self):
        """Test execute avec valeurs None"""
        self.command_router.execute(None, None, None)
        self.command_router.console.print.assert_called_once_with(
            "[red]Commande non trouvée: None/None/None[/red]"
        )
