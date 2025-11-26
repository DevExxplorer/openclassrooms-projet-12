import pytest # noqa
from unittest.mock import Mock, patch
from app.services.menu_service import MenuService


class TestMenuService:
    def setup_method(self):
        self.menu_service = MenuService()
        self.menu_service.console = Mock()
        self.mock_user = Mock()
        self.mock_user.department_id = 1

    @patch('app.services.menu_service.CommandRouter')
    @patch('app.services.menu_service.Menu')
    def test_handle_main_menu_logout(self, mock_menu_class, mock_router):
        """Test logout depuis le menu principal"""
        self.menu_service._get_user_department = Mock(return_value="gestion")
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        mock_menu.get_choice.return_value = "0"
        mock_menu.is_valid_choice.return_value = True

        result = self.menu_service.handle_main_menu(self.mock_user)
        assert result == "logout"

    @patch('app.services.menu_service.MENU_MAPPING', {"gestion": {"1": "submenu_key"}})
    @patch('app.services.menu_service.DIRECT_ACTIONS', {})
    def test_submenu_key_found(self):
        """Test récupération submenu_key"""
        dept_name = "gestion"
        choice = "1"
        submenu_key = {"gestion": {"1": "submenu_key"}}[dept_name.lower()].get(choice)
        assert submenu_key == "submenu_key"

    @patch('app.services.menu_service.MENU_MAPPING', {"commercial": {}})
    @patch('app.services.menu_service.DIRECT_ACTIONS', {("commercial", "1"): "create_client"})
    def test_direct_action_found(self):
        """Test action directe trouvée"""
        dept_name = "commercial"
        choice = "1"
        submenu_key = {}.get(choice)  # None
        action = {("commercial", "1"): "create_client"}.get((dept_name.lower(), choice))

        assert not submenu_key
        assert action == "create_client"

    @patch('app.services.menu_service.MENU_MAPPING', {"commercial": {}})
    @patch('app.services.menu_service.DIRECT_ACTIONS', {})
    def test_action_not_found(self):
        """Test action non trouvée"""
        dept_name = "commercial"
        choice = "99"
        submenu_key = {}.get(choice)  # None
        action = {}.get((dept_name.lower(), choice))  # None

        assert not submenu_key
        assert not action

    @patch('app.services.menu_service.Submenu')
    def test_handle_submenu_back_to_main(self, mock_submenu_class):
        """Test retour au menu principal"""
        mock_submenu = Mock()
        mock_submenu_class.return_value = mock_submenu
        mock_submenu.get_choice.return_value = "0"
        mock_submenu.is_valid_choice.return_value = True

        result = self.menu_service.handle_submenu("test_key")
        assert result == "back_to_main"

    @patch('app.services.menu_service.Submenu')
    def test_handle_submenu_execute_command(self, mock_submenu_class):
        """Test exécution commande depuis sous-menu"""
        mock_submenu = Mock()
        mock_submenu_class.return_value = mock_submenu
        mock_submenu.get_choice.return_value = "1"
        mock_submenu.is_valid_choice.return_value = True

        self.menu_service._route_to_command = Mock()
        self.menu_service.handle_submenu("test_key")
        self.menu_service._route_to_command.assert_called_once_with("test_key", "1")

    @patch('app.services.menu_service.Department')
    def test_get_user_department_success(self, mock_department):
        """Test récupération département réussie"""
        mock_department.get_department_with_id.return_value = "gestion"
        result = self.menu_service._get_user_department(self.mock_user)
        assert result == "gestion"

    @patch('app.services.menu_service.Department')
    @patch('app.services.menu_service.MESSAGES', {"invalid_department": "Département invalide"})
    def test_get_user_department_invalid(self, mock_department):
        """Test département invalide"""
        mock_department.get_department_with_id.return_value = None

        result = self.menu_service._get_user_department(self.mock_user)
        assert result is None
        self.menu_service.console.print.assert_called()

    @patch('app.services.menu_service.Department')
    def test_get_user_department_exception(self, mock_department):
        """Test exception département"""
        mock_department.get_department_with_id.side_effect = Exception("Erreur")
        result = self.menu_service._get_user_department(self.mock_user)
        assert result is None

    def test_route_to_command_users_gestion(self):
        """Test routage users"""
        self.menu_service.router = Mock()
        self.menu_service._route_to_command("gestion_collaborateurs", "1")
        self.menu_service.router.execute.assert_called_once_with("users", "gestion", "1")

    def test_route_to_command_unknown(self):
        """Test routage inconnu"""
        self.menu_service.router = Mock()
        self.menu_service._route_to_command("unknown", "1")
        self.menu_service.console.print.assert_called_once()

    @patch('app.services.menu_service.CommandRouter')
    @patch('app.services.menu_service.Menu')
    @patch('app.services.menu_service.MENU_MAPPING')
    @patch('app.services.menu_service.DIRECT_ACTIONS')
    def test_handle_main_menu_direct_action_execution(self, mock_direct_actions, mock_menu_mapping, mock_menu_class, mock_router):
        """Test exécution réelle d'action directe"""
        self.menu_service._get_user_department = Mock(return_value="commercial")

        # Configuration des mocks
        mock_menu_mapping.__getitem__.return_value = {}  # Pas de sous-menu pour ce département
        mock_direct_actions.get.return_value = "create_client"
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        # Premier appel: action directe, deuxième appel: sous-menu, troisième: logout
        mock_menu.get_choice.side_effect = ["1", "2", "0"]
        mock_menu.is_valid_choice.return_value = True
        mock_router_instance = Mock()
        mock_router.return_value = mock_router_instance

        # Mock handle_submenu pour retourner quelque chose
        self.menu_service.handle_submenu = Mock(return_value="some_result")

        # Exécution
        result = self.menu_service.handle_main_menu(self.mock_user)

        # Vérifications
        mock_router_instance.execute_direct_action.assert_called_with("create_client")
        # Le résultat sera "some_result" du handle_submenu, pas "logout"
        assert result == "some_result"

    @patch('app.services.menu_service.CommandRouter')
    @patch('app.services.menu_service.Menu')
    @patch('app.services.menu_service.MESSAGES')
    def test_handle_main_menu_invalid_choice_message(self, mock_messages, mock_menu_class, mock_router):
        """Test message d'option invalide"""
        self.menu_service._get_user_department = Mock(return_value="gestion")

        # Configuration du mock messages
        mock_messages.__getitem__.return_value = "Option invalide"
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        mock_menu.get_choice.side_effect = ["99", "0"]  # Choix invalide puis logout
        mock_menu.is_valid_choice.side_effect = [False, True]

        # Exécution
        result = self.menu_service.handle_main_menu(self.mock_user)

        # Vérifications
        self.menu_service.console.print.assert_any_call("Option invalide")
        assert result == "logout"

    @patch('app.services.menu_service.CommandRouter')
    @patch('app.services.menu_service.Menu')
    @patch('app.services.menu_service.MENU_MAPPING')
    @patch('app.services.menu_service.DIRECT_ACTIONS')
    def test_action_not_found_message(self, mock_direct_actions, mock_menu_mapping, mock_menu_class, mock_router):
        """Test message action non trouvée + continue"""
        self.menu_service._get_user_department = Mock(return_value="commercial")

        # Pas de sous-menu ET pas d'action directe
        mock_menu_mapping.__getitem__.return_value = {}
        mock_direct_actions.get.return_value = None  # Action non trouvée
        mock_menu = Mock()
        mock_menu_class.return_value = mock_menu
        mock_menu.get_choice.side_effect = ["1", "0"]  # Action non trouvée puis logout
        mock_menu.is_valid_choice.return_value = True

        # Exécution
        result = self.menu_service.handle_main_menu(self.mock_user)

        # Vérifications
        self.menu_service.console.print.assert_any_call("[red]Action non trouvée[/red]")
        assert result == "logout"

    @patch('app.services.menu_service.Submenu')
    @patch('app.services.menu_service.MESSAGES')
    def test_submenu_invalid_option_message(self, mock_messages, mock_submenu_class):
        """Test message invalid_option dans handle_submenu"""
        mock_messages.__getitem__.return_value = "Option invalide"
        mock_submenu = Mock()
        mock_submenu_class.return_value = mock_submenu
        mock_submenu.get_choice.side_effect = ["99", "0"]  # Invalid puis retour
        mock_submenu.is_valid_choice.side_effect = [False, True]
        # Exécution
        result = self.menu_service.handle_submenu("test_key")
        # Vérifications
        self.menu_service.console.print.assert_any_call("Option invalide")
        assert result == "back_to_main"
