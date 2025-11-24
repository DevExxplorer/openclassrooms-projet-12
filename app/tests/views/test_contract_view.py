import pytest # noqa
from unittest.mock import Mock, patch
from datetime import datetime
from app.views.contract import ContractView


class TestContractView:
    def setup_method(self):
        self.contract_view = ContractView()
        self.contract_view.console = Mock()

    @patch('app.views.contract.ClientCommands')
    @patch('app.views.contract.Prompt')
    def test_get_contract_creation_form(self, mock_prompt, mock_client_commands):
        """Test formulaire création contrat"""
        mock_prompt.ask.side_effect = ["1", "1000", "500", "signé"]
        result = self.contract_view.get_contract_creation_form()

        assert result == {
            'client_id': "1",
            'total_amount': "1000",
            'remaining_amount': "500",
            'status': "signé"
        }

    def test_get_contract_id_valid(self):
        """Test récupération ID contrat valide"""
        self.contract_view.console.input.return_value = " 123 "
        result = self.contract_view.get_contract_id()
        assert result == 123

    def test_get_contract_id_invalid(self):
        """Test récupération ID contrat invalide"""
        self.contract_view.console.input.return_value = "abc"
        result = self.contract_view.get_contract_id()
        assert result is None

    @patch('app.views.contract.Prompt')
    def test_get_contract_update_form(self, mock_prompt):
        """Test formulaire mise à jour"""
        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.total_amount = 1000
        mock_contract.remaining_amount = 500
        mock_contract.is_signed = True
        mock_prompt.ask.side_effect = ["2000", "1000", "non signé"]
        result = self.contract_view.get_contract_update_form(mock_contract)

        assert result == {
            'total_amount': 2000.0,
            'remaining_amount': 1000.0,
            'is_signed': False
        }

    def test_display_contract_list_empty(self):
        """Test affichage contrats vide"""
        self.contract_view.display_contract_list([])
        self.contract_view.console.print.assert_called()

    def test_display_contract_list_with_data(self):
        """Test affichage contrats avec données"""
        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.client.name = "Test Client"
        mock_contract.commercial_contact.name = "Test Commercial"
        mock_contract.total_amount = 1000
        mock_contract.remaining_amount = 500
        mock_contract.is_signed = True
        mock_contract.created_at.strftime.return_value = "01-01-2024"
        mock_contract.last_updated_at.strftime.return_value = "01-01-2024"

        self.contract_view.display_contract_list([mock_contract])
        self.contract_view.console.print.assert_called()

    def test_research_contract(self):
        """Test recherche contrat"""
        self.contract_view.console.input.return_value = " 123 "
        result = self.contract_view.research_contract()
        assert result == "123"

    def test_get_date_filter_valid(self):
        """Test filtre date valide"""
        self.contract_view.console.input.return_value = "01-01-2024"
        result = self.contract_view.get_date_filter()
        assert result == datetime(2024, 1, 1)

    def test_get_date_filter_invalid(self):
        """Test filtre date invalide"""
        self.contract_view.console.input.return_value = "invalid"
        result = self.contract_view.get_date_filter()
        assert result is None

    def test_get_amount_filter_valid(self):
        """Test filtre montant valide"""
        self.contract_view.console.input.return_value = " 1000.50 "
        result = self.contract_view.get_amount_filter()
        assert result == 1000.50

    def test_get_amount_filter_invalid(self):
        """Test filtre montant invalide"""
        self.contract_view.console.input.return_value = "abc"
        result = self.contract_view.get_amount_filter()
        assert result is None

    @patch('app.views.contract.UserCommands')
    @patch('app.views.contract.Prompt')
    def test_get_commercial_id(self, mock_prompt, mock_user_commands):
        """Test récupération ID commercial"""
        mock_prompt.ask.return_value = "5"
        result = self.contract_view.get_commercial_id()

        assert result == "5"
        mock_user_commands.assert_called_once()

    def test_display_contract_list_unsigned(self):
        """Test affichage contrat non signé"""
        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.client.name = "Test Client"
        mock_contract.commercial_contact.name = "Test Commercial"
        mock_contract.total_amount = 1000
        mock_contract.remaining_amount = 500
        mock_contract.is_signed = False  # ← Non signé pour tester l'else
        mock_contract.created_at.strftime.return_value = "01-01-2024"
        mock_contract.last_updated_at.strftime.return_value = "01-01-2024"

        self.contract_view.display_contract_list([mock_contract])
        self.contract_view.console.print.assert_called()
