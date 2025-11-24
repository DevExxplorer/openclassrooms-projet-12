import pytest
from unittest.mock import Mock, patch, MagicMock

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

    @patch('app.commands.contract.Contract')
    @patch('app.commands.contract.db_manager')
    def test_create_contract_success(self, mock_db_manager, mock_contract):
        """Test création de contrat réussie"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_client = Mock()
        mock_client.commercial_contact_id = 1
        mock_client.commercial_contact.name = "Commercial Test"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_client

        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 1,
            'total_amount': 1000.0,
            'remaining_amount': 500.0
        }

        mock_contract_instance = Mock()
        mock_contract_instance.id = 123
        mock_contract.create.return_value = mock_contract_instance

        self.contract_commands.create_contract()

        mock_contract.create.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_create_contract_client_not_found(self, mock_db_manager):
        """Test création avec client introuvable"""

        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 999
        }

        self.contract_commands.create_contract()

        mock_session.close.assert_called_once()
        self.contract_commands.console.print.assert_called()

    @patch('app.commands.contract.db_manager')
    def test_update_contract_success(self, mock_db_manager):
        """Test mise à jour de contrat réussie"""

        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_contract = Mock()
        mock_contract.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_contract

        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 1
        self.contract_commands.contract_view.get_contract_update_form.return_value = {
            'total_amount': 2000.0,
            'remaining_amount': 1000.0
        }

        self.contract_commands.update_contract("gestion")

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_update_contract_not_found(self, mock_db_manager):
        """Test mise à jour avec contrat introuvable"""

        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_session.query.return_value.filter.return_value.first.return_value = None

        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 999

        self.contract_commands.update_contract("gestion")

        mock_session.close.assert_called_once()
        self.contract_commands.console.print.assert_called()

    @patch('app.commands.contract.db_manager')
    def test_list_contracts_gestion_role(self, mock_db_manager):
        """Test listage des contrats pour rôle gestion"""

        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_contracts = [Mock(), Mock()]
        mock_session.query.return_value.all.return_value = mock_contracts

        self.contract_commands.contract_view.display_contract_list.return_value = "contracts_displayed"

        result = self.contract_commands.list_contracts("gestion")

        assert result == "contracts_displayed"
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_list_contracts_commercial_role(self, mock_db_manager):
        """Test listage des contrats pour rôle commercial"""

        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_contracts = [Mock()]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_contracts

        self.contract_commands.contract_view.display_contract_list.return_value = "filtered_contracts"

        result = self.contract_commands.list_contracts("commercial")

        assert result == "filtered_contracts"
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_filter_unsigned_contracts(self, mock_db_manager):
        """Test filtrage des contrats non signés"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_contracts = [Mock(), Mock()]
        mock_session.query.return_value.filter.return_value.filter.return_value.all.return_value = mock_contracts

        self.contract_commands.filter_unsigned_contracts()

        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_filter_signed_contracts(self, mock_db_manager):
        """Test filtrage des contrats signés"""

        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_contracts = [Mock()]
        mock_session.query.return_value.filter.return_value.filter.return_value.all.return_value = mock_contracts

        self.contract_commands.filter_signed_contracts()

        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_filter_unpaid_contracts(self, mock_db_manager):
        """Test filtrage des contrats impayés"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_contracts = [Mock(), Mock(), Mock()]
        mock_session.query.return_value.filter.return_value.filter.return_value.all.return_value = mock_contracts

        self.contract_commands.filter_unpaid_contracts()
        self.contract_commands.contract_view.display_contract_list.assert_called_once_with(mock_contracts)
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_filter_contracts_exception(self, mock_db_manager):
        """Test gestion d'exception dans le filtrage"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("DB Error")

        self.contract_commands.filter_contracts("unsigned")
        self.contract_commands.console.print.assert_called()
        mock_session.close.assert_called_once()

    def test_filter_methods_call_filter_contracts(self):
        """Test que les méthodes de filtrage appellent filter_contracts"""
        self.contract_commands.filter_contracts = Mock()
        self.contract_commands.filter_unsigned_contracts()
        self.contract_commands.filter_contracts.assert_called_with("unsigned")
        
        self.contract_commands.filter_signed_contracts()
        self.contract_commands.filter_contracts.assert_called_with("signed")
        
        self.contract_commands.filter_unpaid_contracts()
        self.contract_commands.filter_contracts.assert_called_with("unpaid")

    @patch('app.commands.contract.db_manager')
    def test_create_contract_without_commercial(self, mock_db_manager):
        """Test création avec client sans commercial assigné"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_client = Mock()
        mock_client.commercial_contact_id = None
        mock_session.query.return_value.filter.return_value.first.return_value = mock_client

        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 1,
            'total_amount': 1000.0,
            'remaining_amount': 500.0
        }
        self.contract_commands.contract_view.get_commercial_id.return_value = 2
        self.contract_commands.create_contract()
        self.contract_commands.contract_view.get_commercial_id.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_update_contract_with_empty_string(self, mock_db_manager):
        """Test mise à jour avec chaîne vide (pour couvrir le continue)"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_contract = Mock()
        mock_contract.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_contract
        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 1
        self.contract_commands.contract_view.get_contract_update_form.return_value = {
            'total_amount': 2000.0,
            'location': '   ',
            'remaining_amount': 1000.0
        }

        self.contract_commands.update_contract("gestion")

        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_update_contract_exception_with_rollback(self, mock_db_manager):
        """Test exception lors de la mise à jour avec rollback"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_contract = Mock()
        mock_contract.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_contract
        mock_session.commit.side_effect = Exception("Erreur DB")

        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 1
        self.contract_commands.contract_view.get_contract_update_form.return_value = {
            'total_amount': 2000.0
        }

        self.contract_commands.update_contract("gestion")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        self.contract_commands.console.print.assert_called()

    @patch('app.commands.contract.Contract')
    @patch('app.commands.contract.db_manager')
    def test_create_contract_exception(self, mock_db_manager, mock_contract):
        """Test exception lors de la création de contrat"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        mock_client = Mock()
        mock_client.commercial_contact_id = 1
        mock_client.commercial_contact.name = "Commercial Test"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_client

        self.contract_commands.contract_view.get_contract_creation_form.return_value = {
            'client_id': 1,
            'total_amount': 1000.0,
            'remaining_amount': 500.0
        }

        mock_contract.create.side_effect = Exception("Erreur création")

        self.contract_commands.create_contract()
        self.contract_commands.console.print.assert_called()
        mock_session.close.assert_called_once()

    @patch('app.commands.contract.db_manager')
    def test_list_contracts_exception(self, mock_db_manager):
        """Test exception dans list_contracts"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("Erreur DB dans list_contracts")
        result = self.contract_commands.list_contracts("gestion")
        self.contract_commands.console.print.assert_called()
        mock_session.close.assert_called_once()
        assert result is None

    @patch('app.commands.contract.db_manager')
    def test_update_contract_query_exception(self, mock_db_manager):
        """Test exception lors de la requête dans update_contract"""
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("Erreur query")
        self.contract_commands.list_contracts = Mock()
        self.contract_commands.contract_view.get_contract_id.return_value = 1
        self.contract_commands.update_contract("gestion")

        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        self.contract_commands.console.print.assert_called()
