import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner

from app.controllers.cli import main_cli, show_menu, initialize_database


class TestCLI:
    """Tests pour le CLI principal"""

    def test_main_cli_with_dev_init(self):
        """Test du CLI avec l'option --dev-init"""
        runner = CliRunner()

        with patch('app.commands.cli.initialize_database') as mock_init:
            mock_init.return_value = True

            result = runner.invoke(main_cli, ['--dev-init'])

            assert result.exit_code == 0
            mock_init.assert_called_once()

    def test_main_cli_normal(self):
        """Test du CLI normal (sans options)"""
        runner = CliRunner()

        with patch('app.commands.cli.main_loop') as mock_main_loop:
            result = runner.invoke(main_cli)

            assert result.exit_code == 0
            mock_main_loop.assert_called_once()


class TestInitializeDatabase:
    """Tests pour l'initialisation de la base de données"""

    @patch('app.commands.cli.Initialization')
    @patch('app.commands.cli.console')
    def test_initialize_database_success(self, mock_console, mock_initialization):
        """Test initialisation réussie"""
        mock_initialization.initialize_application.return_value = {
            'errors': []
        }
        result = initialize_database()

        assert result is True
        mock_initialization.initialize_application.assert_called_once()

    @patch('app.commands.cli.Initialization')
    @patch('app.commands.cli.console')
    def test_initialize_database_with_errors(self, mock_console, mock_initialization):
        """Test initialisation avec erreurs"""
        mock_initialization.initialize_application.return_value = {
            'errors': ['Erreur 1', 'Erreur 2']
        }

        result = initialize_database()

        assert result is False
        mock_initialization.initialize_application.assert_called_once()


class TestShowMenu:
    """Tests pour le menu principal"""

    @patch('app.commands.cli.MenuService')
    @patch('app.commands.cli.AuthService')
    @patch('app.commands.cli.console')
    def test_show_menu_invalid_user(self, mock_console, mock_auth_service, mock_menu_service):
        """Test avec utilisateur invalide"""
        # Mock de l'authentification qui échoue
        mock_auth_instance = Mock()
        mock_auth_instance.authenticate_user.return_value = None
        mock_auth_service.return_value = mock_auth_instance

        result = show_menu()

        assert result == "continue"
        mock_auth_instance.authenticate_user.assert_called_once()

    @patch('app.commands.cli.MenuService')
    @patch('app.commands.cli.AuthService')
    @patch('app.commands.cli.console')
    def test_show_menu_success_then_exit(self, mock_console, mock_auth_service, mock_menu_service):
        """Test avec authentification réussie puis exit"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.name = "Test User"

        # Mock de l'authentification réussie
        mock_auth_instance = Mock()
        mock_auth_instance.authenticate_user.return_value = mock_user
        mock_auth_service.return_value = mock_auth_instance

        # Mock du menu qui retourne exit
        mock_menu_instance = Mock()
        mock_menu_instance.handle_main_menu.return_value = "exit"
        mock_menu_service.return_value = mock_menu_instance

        result = show_menu()

        assert result == "exit"
        mock_auth_instance.authenticate_user.assert_called_once()
        mock_menu_instance.handle_main_menu.assert_called_once_with(mock_user)

    @patch('app.commands.cli.MenuService')
    @patch('app.commands.cli.AuthService')
    @patch('app.commands.cli.console')
    def test_show_menu_logout(self, mock_console, mock_auth_service, mock_menu_service):
        """Test avec logout"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.name = "Test User"

        # Mock de l'authentification réussie
        mock_auth_instance = Mock()
        mock_auth_instance.authenticate_user.return_value = mock_user
        mock_auth_service.return_value = mock_auth_instance

        # Mock du menu qui retourne logout
        mock_menu_instance = Mock()
        mock_menu_instance.handle_main_menu.return_value = "logout"
        mock_menu_service.return_value = mock_menu_instance

        result = show_menu()

        assert result == "continue"
        mock_auth_instance.logout.assert_called_once()

    @patch('app.commands.cli.MenuService')
    @patch('app.commands.cli.AuthService') 
    @patch('app.commands.cli.console')
    @patch('app.commands.cli.DIRECT_ACTIONS', {'action1': 'direct_action_1'})
    def test_show_menu_direct_action(self, mock_console, mock_auth_service, mock_menu_service):
        """Test avec action directe puis exit"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.name = "Test User"

        # Mock de l'authentification réussie
        mock_auth_instance = Mock()
        mock_auth_instance.authenticate_user.return_value = mock_user
        mock_auth_service.return_value = mock_auth_instance

        # Mock du menu et router
        mock_router = Mock()
        mock_menu_instance = Mock()
        mock_menu_instance.router = mock_router

        # Première fois retourne action directe, deuxième fois exit
        mock_menu_instance.handle_main_menu.side_effect = ["direct_action_1", "exit"]
        mock_menu_service.return_value = mock_menu_instance

        result = show_menu()

        assert result == "exit"
        mock_router.execute_direct_action.assert_called_once_with("direct_action_1")


class TestMainLoop:
    """Tests pour la boucle principale"""

    @patch('app.commands.cli.show_menu')
    def test_main_loop_exit(self, mock_show_menu):
        """Test de la boucle principale avec exit"""

        mock_show_menu.return_value = "exit"

        from app.controllers.cli import main_loop

        main_loop()
        
        mock_show_menu.assert_called_once()

    @patch('app.commands.cli.show_menu')
    def test_main_loop_continue_then_exit(self, mock_show_menu):
        """Test de la boucle principale avec continue puis exit"""

        mock_show_menu.side_effect = ["continue", "exit"]

        from app.controllers.cli import main_loop

        main_loop()

        assert mock_show_menu.call_count == 2
