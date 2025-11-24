import pytest # noqa
from unittest.mock import Mock, patch
from app.views.user import userView


class TestUserView:
    def setup_method(self):
        self.user_view = userView()
        self.user_view.console = Mock()

    @patch('app.views.user.Prompt')
    def test_get_user_creation_form(self, mock_prompt):
        """Test formulaire création utilisateur"""
        mock_prompt.ask.side_effect = [
            "John Doe", "john@test.com", "johndoe", "password123", "commercial"
        ]

        result = self.user_view.get_user_creation_form()

        assert result == {
            'name': "John Doe", 'mail': "john@test.com", 'username': "johndoe",
            'password': "password123", 'department': "commercial"
        }

    @patch('app.views.user.Prompt')
    def test_get_user_id(self, mock_prompt):
        """Test récupération ID utilisateur"""
        mock_prompt.ask.return_value = "123"
        result = self.user_view.get_user_id()
        assert result == 123

    @patch('app.views.user.Prompt')
    def test_get_user_update_form(self, mock_prompt):
        """Test formulaire mise à jour utilisateur"""
        mock_user = Mock()
        mock_user.name = "Old"
        mock_user.mail = "old@test.com"
        mock_user.username = "old"
        mock_user.department.name = "support"

        mock_prompt.ask.side_effect = ["New", "new@test.com", "new", "gestion"]
        result = self.user_view.get_user_update_form(mock_user)

        assert result['name'] == "New"

    def test_display_user_list_empty(self):
        """Test affichage utilisateurs vide"""
        self.user_view.display_user_list([])
        self.user_view.console.print.assert_called()

    def test_display_user_list_with_data(self):
        """Test affichage utilisateurs avec données"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.employee_number = "EMP001"
        mock_user.name = "John"
        mock_user.mail = "john@test.com"
        mock_user.department.name = "commercial"
        mock_user.created_at.strftime.return_value = "01/01/2024"

        self.user_view.display_user_list([mock_user])
        self.user_view.console.print.assert_called()

    def test_display_user_list_with_null_data(self):
        """Test affichage avec données nulles"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.employee_number = "EMP001"
        mock_user.name = "John"
        mock_user.mail = "john@test.com"
        mock_user.department = None
        mock_user.created_at = None

        self.user_view.display_user_list([mock_user])
        self.user_view.console.print.assert_called()
