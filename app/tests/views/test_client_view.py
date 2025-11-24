import pytest # noqa
from unittest.mock import Mock, patch
from app.views.client import ClientView


class TestClientView:
    def setup_method(self):
        self.client_view = ClientView()
        self.client_view.console = Mock()

    def test_get_client_creation_form(self):
        """Test formulaire création client"""
        self.client_view.console.input.side_effect = ["Test Client", "test@test.com", "+33123456789", "Test Corp"]
        result = self.client_view.get_client_creation_form()

        assert result == {
            "name": "Test Client",
            "mail": "test@test.com",
            "phone": "+33123456789",
            "company_name": "Test Corp"
        }

    def test_display_clients_empty(self):
        """Test affichage clients vide"""
        self.client_view.display_clients([])
        self.client_view.console.print.assert_called()

    def test_display_clients_with_data(self):
        """Test affichage clients avec données"""
        mock_client = Mock()
        mock_client.id = 1
        mock_client.name = "Test"
        mock_client.mail = "test@test.com"
        mock_client.phone = "+33123456789"
        mock_client.company_name = "Test Corp"
        mock_client.commercial_contact_id = 1
        mock_client.created_at.strftime.return_value = "01-01-2024"
        mock_client.last_updated_at.strftime.return_value = "01-01-2024"

        self.client_view.display_clients([mock_client])
        self.client_view.console.print.assert_called()

    def test_get_id_client(self):
        """Test récupération ID client"""
        self.client_view.console.input.return_value = " 123 "
        result = self.client_view.get_id_client()
        assert result == "123"

    @patch('app.views.client.Prompt')
    def test_get_client_update_form(self, mock_prompt):
        """Test formulaire mise à jour"""
        mock_client = Mock()
        mock_client.name = "Old Name"
        mock_client.mail = "old@test.com"
        mock_client.phone = "+33987654321"
        mock_client.company_name = "Old Corp"
        mock_prompt.ask.side_effect = ["New Name", "new@test.com", "+33111111111", "New Corp"]

        result = self.client_view.get_client_update_form(mock_client)
        assert result == {
            "name": "New Name",
            "mail": "new@test.com",
            "phone": "+33111111111",
            "company_name": "New Corp"
        }

    def test_research_client(self):
        """Test recherche client"""
        self.client_view.console.input.return_value = " Test Search "
        result = self.client_view.research_client()
        assert result == "Test Search"
