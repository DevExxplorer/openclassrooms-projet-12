import pytest  # noqa
from unittest.mock import Mock, patch

from app.controllers.client import ClientCommands


class TestClientCommands:
    """Tests pour ClientCommands"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.name = "Test User"

        self.client_commands = ClientCommands(current_user=self.mock_user, role="commercial")
        self.client_commands.view = Mock()
        self.client_commands.console = Mock()

    @patch('app.controllers.client.Client')
    def test_create_client_success(self, mock_client):
        """Test création de client réussie"""
        self.client_commands.view.get_client_creation_form.return_value = {
            'name': 'Client Test',
            'mail': 'client@test.com',
            'phone': '+33123456789',
            'company_name': 'Test Company'
        }
        mock_client_instance = Mock()
        mock_client_instance.name = "Client Test"
        mock_client.create.return_value = mock_client_instance

        self.client_commands.create_client()

        expected_data = {
            'name': 'Client Test',
            'mail': 'client@test.com',
            'phone': '+33123456789',
            'company_name': 'Test Company',
            'commercial_contact_id': 1
        }
        mock_client.create.assert_called_once_with('commercial', **expected_data)
        self.client_commands.console.print.assert_called()

    @patch('app.controllers.client.Client')
    def test_create_client_exception(self, mock_client):
        """Test exception lors de la création de client"""
        self.client_commands.view.get_client_creation_form.return_value = {
            'name': 'Client Test',
            'mail': 'client@test.com'
        }
        mock_client.create.side_effect = Exception("Erreur création client")

        self.client_commands.create_client()

        self.client_commands.console.print.assert_called()

    @patch('app.controllers.client.Client')
    def test_list_clients_gestion_role(self, mock_client):
        """Test listage des clients pour rôle gestion"""
        mock_clients = [Mock(), Mock()]
        mock_client.get_all.return_value = mock_clients

        self.client_commands.list_clients("gestion")

        mock_client.get_all.assert_called_once()
        self.client_commands.view.display_clients.assert_called_once_with(mock_clients)

    @patch('app.controllers.client.Client')
    def test_list_clients_commercial_role(self, mock_client):
        """Test listage des clients pour rôle commercial"""
        mock_clients = [Mock()]
        mock_client.get_by_commercial.return_value = mock_clients

        self.client_commands.list_clients("commercial")

        mock_client.get_by_commercial.assert_called_once_with(1)
        self.client_commands.view.display_clients.assert_called_once_with(mock_clients)

    @patch('app.controllers.client.Client')
    def test_update_client_success(self, mock_client):
        """Test mise à jour de client réussie"""
        mock_client_instance = Mock()
        mock_client_instance.id = 1
        mock_client_instance.name = "Client Test"
        mock_client.get_by_id_with_permissions.return_value = mock_client_instance

        self.client_commands.view.get_id_client.return_value = 1
        self.client_commands.view.get_client_update_form.return_value = {
            'name': 'Nouveau Nom',
            'mail': 'nouveau@test.com'
        }

        self.client_commands.update_client()

        mock_client.get_by_id_with_permissions.assert_called_once_with(1, 1)
        mock_client_instance.update.assert_called_once()
        self.client_commands.console.print.assert_called()

    @patch('app.controllers.client.Client')
    def test_update_client_not_found(self, mock_client):
        """Test mise à jour avec client introuvable"""
        mock_client.get_by_id_with_permissions.return_value = None

        self.client_commands.view.get_id_client.return_value = 999

        self.client_commands.update_client()

        mock_client.get_by_id_with_permissions.assert_called_once_with(999, 1)
        self.client_commands.console.print.assert_called()

    @patch('app.controllers.client.Client')
    def test_update_client_with_empty_values(self, mock_client):
        """Test mise à jour avec valeurs vides"""
        mock_client_instance = Mock()
        mock_client_instance.id = 1
        mock_client_instance.name = "Client Test"
        mock_client.get_by_id_with_permissions.return_value = mock_client_instance

        self.client_commands.view.get_id_client.return_value = 1
        self.client_commands.view.get_client_update_form.return_value = {
            'name': 'Nouveau Nom',
            'description': '   ',
            'mail': 'nouveau@test.com'
        }

        self.client_commands.update_client()

        mock_client_instance.update.assert_called_once()
        self.client_commands.console.print.assert_called()

    @patch('app.controllers.client.Client')
    def test_update_client_exception(self, mock_client):
        """Test exception lors de la mise à jour"""
        mock_client_instance = Mock()
        mock_client_instance.update.side_effect = Exception("Erreur DB")
        mock_client.get_by_id_with_permissions.return_value = mock_client_instance

        self.client_commands.view.get_id_client.return_value = 1
        self.client_commands.view.get_client_update_form.return_value = {
            'name': 'Nouveau Nom'
        }

        self.client_commands.update_client()

        self.client_commands.console.print.assert_called()

    @patch('app.controllers.client.Client')
    def test_research_client_success(self, mock_client):
        """Test recherche de client réussie"""
        mock_clients = [Mock(), Mock()]
        mock_client.search_by_name.return_value = mock_clients

        self.client_commands.view.research_client.return_value = "Test"

        self.client_commands.research_client()

        mock_client.search_by_name.assert_called_once_with("Test")
        self.client_commands.view.display_clients.assert_called_once_with(mock_clients)

    @patch('app.controllers.client.Client')
    def test_research_client_no_results(self, mock_client):
        """Test recherche de client sans résultats"""
        mock_client.search_by_name.return_value = []

        self.client_commands.view.research_client.return_value = "Inexistant"

        self.client_commands.research_client()

        mock_client.search_by_name.assert_called_once_with("Inexistant")
        self.client_commands.view.display_clients.assert_called_once_with([])

    def test_init_with_parameters(self):
        """Test du constructeur avec paramètres"""
        user = Mock()
        user.id = 2

        client_commands = ClientCommands(current_user=user, role="gestion")

        assert client_commands.current_user == user
        assert client_commands.role == "gestion"

    def test_init_without_parameters(self):
        """Test du constructeur sans paramètres"""
        client_commands = ClientCommands()

        assert client_commands.current_user is None
        assert client_commands.role is None

    @patch('app.controllers.client.Client')
    def test_list_clients_support_role(self, mock_client):
        """Test listage des clients pour rôle support"""
        mock_clients = [Mock(), Mock(), Mock()]
        mock_client.get_all.return_value = mock_clients

        self.client_commands.list_clients("support")

        mock_client.get_all.assert_called_once()
        self.client_commands.view.display_clients.assert_called_once_with(mock_clients)
