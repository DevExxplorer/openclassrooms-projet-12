import pytest  # noqa
from unittest.mock import Mock, patch

from app.controllers.contract import ContractCommands


class TestContractCommands:
    """Tests pour ContractCommands"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.name = "Test User"

        self.contract_commands = ContractCommands(current_user=self.mock_user)
        self.contract_commands.contract_view = Mock()
        self.contract_commands.console = Mock()

    @patch('app.controllers.contract.Contract')
    def test_create_contract_success(self, mock_contract):
        """Test création de contrat réussie"""
        # Mock des données du formulaire
        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 1,
            'total_amount': 1000.0,
            'remaining_amount': 500.0,
            'status': 'signé'
        }

        # Mock du client avec commercial
        mock_client = Mock()
        mock_client.commercial_contact_id = 1
        mock_client.commercial_contact.name = "Commercial Test"
        mock_contract.get_client_with_commercial.return_value = mock_client

        # Mock du contrat créé
        mock_contract_instance = Mock()
        mock_contract_instance.id = 123
        mock_contract.create.return_value = mock_contract_instance

        self.contract_commands.create_contract()

        mock_contract.get_client_with_commercial.assert_called_once_with(1)
        mock_contract.create.assert_called_once()
        self.contract_commands.console.print.assert_called()

    @patch('app.controllers.contract.Contract')
    def test_create_contract_client_not_found(self, mock_contract):
        """Test création avec client introuvable"""
        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 999
        }

        mock_contract.get_client_with_commercial.return_value = None

        self.contract_commands.create_contract()

        self.contract_commands.console.print.assert_called()

    @patch('app.controllers.contract.Contract')
    def test_update_contract_success(self, mock_contract):
        """Test mise à jour de contrat réussie"""
        # Mock du contrat existant
        mock_contract_instance = Mock()
        mock_contract_instance.id = 1
        mock_contract.get_by_id_with_permissions.return_value = mock_contract_instance

        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 1
        self.contract_commands.contract_view.get_contract_update_form.return_value = {
            'total_amount': 2000.0,
            'remaining_amount': 1000.0
        }

        self.contract_commands.update_contract("gestion")

        mock_contract.get_by_id_with_permissions.assert_called_once_with(1, 1, "gestion")
        mock_contract_instance.update.assert_called_once()
        self.contract_commands.console.print.assert_called()

    @patch('app.controllers.contract.Contract')
    def test_update_contract_not_found(self, mock_contract):
        """Test mise à jour avec contrat introuvable"""
        mock_contract.get_by_id_with_permissions.return_value = None

        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 999

        self.contract_commands.update_contract("gestion")

        self.contract_commands.console.print.assert_called()

    @patch('app.controllers.contract.Contract')
    def test_list_contracts_gestion_role(self, mock_contract):
        """Test listage des contrats pour rôle gestion"""
        mock_contracts = [Mock(), Mock()]
        mock_contract.get_all.return_value = mock_contracts

        result = self.contract_commands.list_contracts("gestion")

        mock_contract.get_all.assert_called_once()
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)

    @patch('app.controllers.contract.Contract')
    def test_list_contracts_commercial_role(self, mock_contract):
        """Test listage des contrats pour rôle commercial"""
        mock_contracts = [Mock()]
        mock_contract.get_by_commercial.return_value = mock_contracts

        result = self.contract_commands.list_contracts("commercial")

        mock_contract.get_by_commercial.assert_called_once_with(1)
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)

    @patch('app.controllers.contract.Contract')
    def test_filter_unsigned_contracts(self, mock_contract):
        """Test filtrage des contrats non signés"""
        mock_contracts = [Mock(), Mock()]
        mock_contract.get_filtered_contracts.return_value = mock_contracts

        self.contract_commands.filter_unsigned_contracts()

        mock_contract.get_filtered_contracts.assert_called_once_with(1, "unsigned")
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)

    @patch('app.controllers.contract.Contract')
    def test_filter_signed_contracts(self, mock_contract):
        """Test filtrage des contrats signés"""
        mock_contracts = [Mock()]
        mock_contract.get_filtered_contracts.return_value = mock_contracts

        self.contract_commands.filter_signed_contracts()

        mock_contract.get_filtered_contracts.assert_called_once_with(1, "signed")
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)

    @patch('app.controllers.contract.Contract')
    def test_filter_unpaid_contracts(self, mock_contract):
        """Test filtrage des contrats impayés"""
        mock_contracts = [Mock(), Mock(), Mock()]
        mock_contract.get_filtered_contracts.return_value = mock_contracts

        self.contract_commands.filter_unpaid_contracts()

        mock_contract.get_filtered_contracts.assert_called_once_with(1, "unpaid")
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)

    @patch('app.controllers.contract.Contract')
    def test_filter_contracts_exception(self, mock_contract):
        """Test gestion d'exception dans le filtrage"""
        mock_contract.get_filtered_contracts.side_effect = Exception("DB Error")

        self.contract_commands.filter_contracts("unsigned")

        self.contract_commands.console.print.assert_called()

    def test_filter_methods_call_filter_contracts(self):
        """Test que les méthodes de filtrage appellent filter_contracts"""
        self.contract_commands.filter_contracts = Mock()

        self.contract_commands.filter_unsigned_contracts()
        self.contract_commands.filter_contracts.assert_called_with("unsigned")

        self.contract_commands.filter_signed_contracts()
        self.contract_commands.filter_contracts.assert_called_with("signed")

        self.contract_commands.filter_unpaid_contracts()
        self.contract_commands.filter_contracts.assert_called_with("unpaid")

    @patch('app.controllers.contract.Contract')
    def test_create_contract_without_commercial(self, mock_contract):
        """Test création avec client sans commercial assigné"""
        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 1,
            'total_amount': 1000.0,
            'remaining_amount': 500.0
        }

        mock_client = Mock()
        mock_client.commercial_contact_id = None
        mock_contract.get_client_with_commercial.return_value = mock_client

        self.contract_commands.contract_view.get_commercial_id.return_value = 2

        self.contract_commands.create_contract()

        self.contract_commands.contract_view.get_commercial_id.assert_called_once()

    @patch('app.controllers.contract.Contract')
    def test_create_contract_exception(self, mock_contract):
        """Test exception lors de la création de contrat"""
        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 1,
            'total_amount': 1000.0,
            'remaining_amount': 500.0
        }

        mock_client = Mock()
        mock_client.commercial_contact_id = 1
        mock_contract.get_client_with_commercial.return_value = mock_client

        mock_contract.create.side_effect = Exception("Erreur création")

        self.contract_commands.create_contract()

        self.contract_commands.console.print.assert_called()

    @patch('app.controllers.contract.Contract')
    def test_update_contract_exception(self, mock_contract):
        """Test exception lors de la mise à jour"""
        mock_contract_instance = Mock()
        mock_contract_instance.update.side_effect = Exception("Erreur DB")
        mock_contract.get_by_id_with_permissions.return_value = mock_contract_instance

        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 1
        self.contract_commands.contract_view.get_contract_update_form.return_value = {
            'total_amount': 2000.0
        }

        self.contract_commands.update_contract("gestion")

        self.contract_commands.console.print.assert_called()

    @patch('app.controllers.contract.Contract')
    def test_list_contracts_exception(self, mock_contract):
        """Test exception dans list_contracts"""
        mock_contract.get_all.side_effect = Exception("Erreur DB")

        result = self.contract_commands.list_contracts("gestion")

        self.contract_commands.console.print.assert_called()
