import pytest  # noqa
from unittest.mock import Mock, patch

from app.controllers.event import EventCommands


class TestEventCommands:
    """Tests pour EventCommands"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.name = "Test User"
        self.mock_user.department = Mock()
        self.mock_user.department.name = "support"

        self.event_commands = EventCommands(current_user=self.mock_user)
        self.event_commands.event_view = Mock()
        self.event_commands.console = Mock()

    @patch('app.controllers.event.Event')
    @patch('app.controllers.event.Contract')
    @patch('app.controllers.event.ContractCommands')
    def test_create_event_success(self, mock_contract_commands, mock_contract, mock_event):
        """Test création d'événement réussie"""
        # Mock des contrats signés disponibles
        mock_contract.get_filtered_contracts.return_value = [Mock(), Mock()]

        # Mock des commandes de contrat
        mock_contract_instance = Mock()
        mock_contract_commands.return_value = mock_contract_instance

        # Mock de la validation du contrat
        mock_event.validate_contract_access.return_value = True

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView pour la création
        mock_event_data = {
            'name': 'Test Event',
            'contract_id': 1,
            'location': 'Paris',
            'attendees': 50
        }

        # Patcher EventView dans le bon contexte
        with patch('app.controllers.event.EventView') as mock_event_view:
            mock_event_view_instance = Mock()
            mock_event_view.return_value = mock_event_view_instance
            mock_event_view_instance.get_event_creation_form.return_value = mock_event_data

            # Mock de Event.create
            mock_event_instance = Mock()
            mock_event_instance.id = 123
            mock_event.create.return_value = mock_event_instance

            # Exécution
            self.event_commands.create_event()

        # Vérifications
        mock_contract.get_filtered_contracts.assert_called_once_with(1, "signed")
        mock_contract_instance.filter_signed_contracts.assert_called_once()
        mock_event.validate_contract_access.assert_called_once_with("1", 1)
        mock_event.create.assert_called_once()
        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Contract')
    def test_create_event_no_signed_contracts(self, mock_contract):
        """Test création sans contrats signés"""
        # Aucun contrat signé
        mock_contract.get_filtered_contracts.return_value = []

        self.event_commands.create_event()

        mock_contract.get_filtered_contracts.assert_called_once_with(1, "signed")
        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_update_event_success(self, mock_event):
        """Test mise à jour d'événement réussie"""
        # Mock de l'événement existant
        mock_event_instance = Mock()
        mock_event_instance.id = 1
        mock_event.get_event_with_permissions.return_value = mock_event_instance

        self.event_commands.list_events = Mock()
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView pour la mise à jour
        with patch('app.controllers.event.EventView') as mock_event_view:
            mock_event_view_instance = Mock()
            mock_event_view.return_value = mock_event_view_instance
            mock_event_view_instance.get_event_update_form.return_value = {
                'name': 'Updated Event',
                'location': 'Lyon'
            }

            self.event_commands.update_event()

        # Vérifications
        mock_event.get_event_with_permissions.assert_called_once_with(1, 1, "support")
        mock_event_instance.update.assert_called_once()
        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_update_event_not_found(self, mock_event):
        """Test mise à jour avec événement introuvable"""
        mock_event.get_event_with_permissions.return_value = None

        self.event_commands.list_events = Mock()
        self.event_commands.console.input.return_value = "999"

        self.event_commands.update_event()

        self.event_commands.console.print.assert_called()

    def test_update_event_invalid_id(self):
        """Test mise à jour avec ID invalide"""
        self.event_commands.list_events = Mock()
        self.event_commands.console.input.return_value = "abc"

        self.event_commands.update_event()

        self.event_commands.console.print.assert_called()

    def test_update_event_unauthorized_role(self):
        """Test mise à jour avec rôle non autorisé"""
        # Changer le département pour un commercial
        self.event_commands.current_user.department.name = "commercial"

        self.event_commands.list_events = Mock()
        self.event_commands.console.input.return_value = "1"

        self.event_commands.update_event()

        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_list_events_gestion_role(self, mock_event):
        """Test listage des événements pour rôle gestion"""
        mock_events = [Mock(), Mock()]
        mock_event.get_all.return_value = mock_events

        self.event_commands.event_view.display_event_list.return_value = "events_displayed"

        result = self.event_commands.list_events(role="gestion")

        assert result == "events_displayed"
        mock_event.get_all.assert_called_once()
        self.event_commands.event_view.display_event_list.assert_called_once_with(mock_events)

    @patch('app.controllers.event.Event')
    def test_list_events_support_role(self, mock_event):
        """Test listage des événements pour rôle support"""
        mock_events = [Mock()]
        mock_event.get_by_support_user.return_value = mock_events

        self.event_commands.event_view.display_event_list.return_value = "filtered_events"

        result = self.event_commands.list_events(role="support")

        assert result == "filtered_events"
        mock_event.get_by_support_user.assert_called_once_with(1)
        self.event_commands.event_view.display_event_list.assert_called_once_with(mock_events)

    @patch('app.controllers.event.Event')
    def test_list_events_with_filter_no_support(self, mock_event):
        """Test listage avec filtre sans support"""
        mock_event_with_support = Mock()
        mock_event_with_support.support_contact = Mock()
        mock_event_without_support = Mock()
        mock_event_without_support.support_contact = None

        mock_events = [mock_event_with_support, mock_event_without_support]
        mock_event.get_all.return_value = mock_events

        self.event_commands.list_events(role="gestion", filter_no_support=True)

        # Vérifications - seuls les événements sans support sont affichés
        expected_filtered = [mock_event_without_support]
        self.event_commands.event_view.display_event_list.assert_called_once_with(expected_filtered)

    @patch('app.controllers.event.Event')
    def test_list_events_exception(self, mock_event):
        """Test exception dans list_events"""
        mock_event.get_all.side_effect = Exception("Erreur DB")

        result = self.event_commands.list_events(role="gestion")

        self.event_commands.console.print.assert_called()
        assert result is None

    @patch('app.controllers.event.Event')
    def test_assign_support_success(self, mock_event):
        """Test assignation de support réussie"""
        # Mock des événements sans support
        mock_events = [Mock()]
        mock_event.get_events_without_support.return_value = mock_events

        # Mock de l'événement à assigner
        mock_event_instance = Mock()
        mock_event_instance.id = 1
        mock_event.get_by_id.return_value = mock_event_instance

        # Mock des supports disponibles
        mock_support = Mock()
        mock_support.id = 2
        mock_support.name = "Support Test"
        mock_event.get_available_supports.return_value = [mock_support]
        mock_event.validate_support_user.return_value = mock_support

        # Mock des méthodes
        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.side_effect = ["1", "2"]

        self.event_commands.assign_support()

        # Vérifications
        mock_event.get_events_without_support.assert_called_once()
        mock_event.get_by_id.assert_called_once_with("1")
        mock_event.get_available_supports.assert_called_once()
        mock_event.validate_support_user.assert_called_once_with("2")
        mock_event_instance.assign_support.assert_called_once_with(2)
        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_assign_support_no_events_without_support(self, mock_event):
        """Test assignation sans événements sans support"""
        mock_event.get_events_without_support.return_value = []

        self.event_commands.assign_support()

        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_assign_support_event_not_found(self, mock_event):
        """Test assignation avec événement introuvable"""
        mock_event.get_events_without_support.return_value = [Mock()]
        mock_event.get_by_id.side_effect = ValueError("Event not found")

        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.return_value = "999"

        self.event_commands.assign_support()

        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_assign_support_no_supports_available(self, mock_event):
        """Test assignation sans supports disponibles"""
        mock_event.get_events_without_support.return_value = [Mock()]
        mock_event.get_by_id.return_value = Mock()
        mock_event.get_available_supports.return_value = []

        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.return_value = "1"

        self.event_commands.assign_support()

        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_assign_support_support_not_found(self, mock_event):
        """Test assignation avec support introuvable"""
        mock_event.get_events_without_support.return_value = [Mock()]
        mock_event.get_by_id.return_value = Mock()
        mock_event.get_available_supports.return_value = [Mock()]
        mock_event.validate_support_user.return_value = None

        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.side_effect = ["1", "999"]

        self.event_commands.assign_support()

        self.event_commands.console.print.assert_called()

    @patch('app.controllers.event.Event')
    def test_filter_events_without_support_success(self, mock_event):
        """Test filtrage des événements sans support"""
        mock_events = [Mock(), Mock()]
        mock_event.get_events_without_support.return_value = mock_events

        self.event_commands.event_view.display_event_list.return_value = "events_without_support"

        result = self.event_commands.filter_events_without_support()

        assert result == "events_without_support"
        mock_event.get_events_without_support.assert_called_once()
        self.event_commands.event_view.display_event_list.assert_called_once_with(mock_events)

    @patch('app.controllers.event.Event')
    def test_filter_events_without_support_no_events(self, mock_event):
        """Test filtrage sans événements sans support"""
        mock_event.get_events_without_support.return_value = []

        result = self.event_commands.filter_events_without_support()

        self.event_commands.console.print.assert_called()
        assert result is None

    @patch('app.controllers.event.Event')
    def test_filter_events_without_support_exception(self, mock_event):
        """Test exception dans filter_events_without_support"""
        mock_event.get_events_without_support.side_effect = Exception("Erreur DB")

        result = self.event_commands.filter_events_without_support()

        self.event_commands.console.print.assert_called()
        assert result is None
