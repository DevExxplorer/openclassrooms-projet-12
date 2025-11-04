import pytest
from unittest.mock import Mock, patch
from app.views.menu import MenuManager, Menu, Submenu


class TestMenuManager:
    
    def setup_method(self):
        self.menu_manager = MenuManager()
        self.menu_manager.console = Mock()

    def test_display(self):
        """Test affichage menu"""
        self.menu_manager.items = [{"option": "1", "title": "Test Option"}]
        self.menu_manager.display()
        self.menu_manager.console.print.assert_called()

    def test_get_choice(self):
        """Test récupération choix"""
        self.menu_manager.console.input.return_value = "1"
        result = self.menu_manager.get_choice()
        assert result == "1"

    def test_is_valid_choice_true(self):
        """Test choix valide"""
        self.menu_manager.items = [{"option": "1", "title": "Test"}]
        assert self.menu_manager.is_valid_choice("1") is True

    def test_is_valid_choice_false(self):
        """Test choix invalide"""
        self.menu_manager.items = [{"option": "1", "title": "Test"}]
        assert self.menu_manager.is_valid_choice("2") is False

    @patch('app.views.menu.MENU', {"gestion": [{"option": "1", "title": "Test"}]})
    def test_menu_init(self):
        """Test initialisation Menu"""
        menu = Menu("gestion")
        assert menu.department == "gestion"
        assert menu.items == [{"option": "1", "title": "Test"}]

    @patch('app.views.menu.SUBMENUS', {"test_key": [{"option": "1", "title": "Test"}]})
    def test_submenu_init(self):
        """Test initialisation Submenu"""
        submenu = Submenu("test_key")
        assert submenu.submenu_key == "test_key"
        assert submenu.items == [{"option": "1", "title": "Test"}]