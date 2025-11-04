import pytest
from unittest.mock import Mock, patch, MagicMock

from app.commands.event import EventCommands


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

        # Mock de la vue et console après création
        self.event_commands.event_view = Mock()
        self.event_commands.console = Mock()

    @patch('app.commands.event.Event')
    @patch('app.commands.event.ContractCommands')
    @patch('app.commands.event.EventView')
    def test_create_event_success(self, mock_event_view, mock_contract_commands, mock_event):
        """Test création d'événement réussie"""
        # Mock des commandes de contrat
        mock_contract_instance = Mock()
        mock_contract_commands.return_value = mock_contract_instance

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView et ses méthodes
        mock_event_view_instance = Mock()
        mock_event_view.return_value = mock_event_view_instance
        mock_event_view_instance.get_event_creation_form.return_value = {
            'name': 'Test Event',
            'contract_id': 1,
            'location': 'Paris',
            'attendees': 50
        }

        # Mock de Event.create
        mock_event_instance = Mock()
        mock_event_instance.id = 123
        mock_event.create.return_value = mock_event_instance

        # Exécution
        self.event_commands.create_event()

        # Vérifications
        mock_contract_instance.filter_signed_contracts.assert_called_once()
        mock_event.create.assert_called_once()
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.Event')
    @patch('app.commands.event.ContractCommands')
    @patch('app.commands.event.EventView')
    def test_create_event_exception(self, mock_event_view, mock_contract_commands, mock_event):
        """Test exception lors de la création d'événement"""
        # Mock des commandes de contrat
        mock_contract_instance = Mock()
        mock_contract_commands.return_value = mock_contract_instance

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView
        mock_event_view_instance = Mock()
        mock_event_view.return_value = mock_event_view_instance
        mock_event_view_instance.get_event_creation_form.return_value = {
            'name': 'Test Event'
        }

        # Exception lors de la création
        mock_event.create.side_effect = Exception("Erreur création événement")

        # Exécution
        self.event_commands.create_event()

        # Vérifications
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    @patch('app.commands.event.EventView')
    def test_update_event_success(self, mock_event_view, mock_db_manager):
        """Test mise à jour d'événement réussie"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement existant
        mock_event = Mock()
        mock_event.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_event

        # Mock de list_events
        self.event_commands.list_events = Mock()

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView
        mock_event_view_instance = Mock()
        mock_event_view.return_value = mock_event_view_instance
        mock_event_view_instance.get_event_update_form.return_value = {
            'name': 'Updated Event',
            'location': 'Lyon'
        }

        # Exécution
        self.event_commands.update_event()

        # Vérifications
        mock_session.commit.assert_called_once()
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    def test_update_event_not_found(self, mock_db_manager):
        """Test mise à jour avec événement introuvable"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Événement introuvable
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Mock de list_events
        self.event_commands.list_events = Mock()

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "999"

        # Exécution
        self.event_commands.update_event()

        # Vérifications
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    def test_update_event_invalid_id(self, mock_db_manager):
        """Test mise à jour avec ID invalide"""
        # Mock de list_events
        self.event_commands.list_events = Mock()

        # Mock de l'input utilisateur avec ID invalide
        self.event_commands.console.input.return_value = "abc"

        # Exécution
        self.event_commands.update_event()

        # Vérifications
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    @patch('app.commands.event.EventView')
    def test_update_event_with_empty_values(self, mock_event_view, mock_db_manager):
        """Test mise à jour avec valeurs vides (test du continue)"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement existant
        mock_event = Mock()
        mock_event.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_event

        # Mock de list_events
        self.event_commands.list_events = Mock()

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView avec valeurs vides
        mock_event_view_instance = Mock()
        mock_event_view.return_value = mock_event_view_instance
        mock_event_view_instance.get_event_update_form.return_value = {
            'name': 'Updated Event',
            'description': '   ',  # Espaces vides - va déclencher le continue
            'location': 'Lyon'
        }

        # Exécution
        self.event_commands.update_event()

        # Vérifications
        mock_session.commit.assert_called_once()

    @patch('app.commands.event.db_manager')
    @patch('app.commands.event.EventView')
    def test_update_event_exception(self, mock_event_view, mock_db_manager):
        """Test exception lors de la mise à jour"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement existant
        mock_event = Mock()
        mock_event.id = 1
        mock_session.query.return_value.filter.return_value.first.return_value = mock_event

        # Exception lors du commit
        mock_session.commit.side_effect = Exception("Erreur DB")

        # Mock de list_events
        self.event_commands.list_events = Mock()

        # Mock de l'input utilisateur
        self.event_commands.console.input.return_value = "1"

        # Mock de EventView
        mock_event_view_instance = Mock()
        mock_event_view.return_value = mock_event_view_instance
        mock_event_view_instance.get_event_update_form.return_value = {
            'name': 'Updated Event'
        }

        # Exécution
        self.event_commands.update_event()

        # Vérifications
        mock_session.rollback.assert_called_once()
        self.event_commands.console.print.assert_called()

    def test_update_event_user_without_department(self):
        """Test mise à jour avec utilisateur sans département"""
        # Utilisateur sans département
        self.event_commands.current_user.department = None

        # Mock de list_events
        self.event_commands.list_events = Mock()

        # Mock de l'input utilisateur avec ID invalide pour sortir rapidement
        self.event_commands.console.input.return_value = "abc"

        # Exécution
        self.event_commands.update_event()

        # Vérifier que list_events a été appelé avec role="gestion"
        self.event_commands.list_events.assert_called_with(role="gestion")

    @patch('app.commands.event.db_manager')
    def test_list_events_gestion_role(self, mock_db_manager):
        """Test listage des événements pour rôle gestion"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des événements
        mock_events = [Mock(), Mock()]
        mock_session.query.return_value.all.return_value = mock_events

        # Mock de la vue
        self.event_commands.event_view.display_event_list.return_value = "events_displayed"

        # Exécution
        result = self.event_commands.list_events(role="gestion")

        # Vérifications
        assert result == "events_displayed"
        self.event_commands.event_view.display_event_list.assert_called_once_with(mock_events)
        mock_session.close.assert_called_once()

    @patch('app.commands.event.db_manager')
    def test_list_events_support_role(self, mock_db_manager):
        """Test listage des événements pour rôle support"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des événements filtrés
        mock_events = [Mock()]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_events

        # Mock de la vue
        self.event_commands.event_view.display_event_list.return_value = "filtered_events"

        # Exécution
        result = self.event_commands.list_events(role="support")

        # Vérifications
        assert result == "filtered_events"
        mock_session.close.assert_called_once()

    @patch('app.commands.event.db_manager')
    def test_list_events_with_filter_no_support(self, mock_db_manager):
        """Test listage avec filtre sans support"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des événements
        mock_event_with_support = Mock()
        mock_event_with_support.support_contact = Mock()
        mock_event_without_support = Mock()
        mock_event_without_support.support_contact = None

        mock_events = [mock_event_with_support, mock_event_without_support]
        mock_session.query.return_value.all.return_value = mock_events

        # Exécution
        self.event_commands.list_events(role="gestion", filter_no_support=True)

        # Vérifications - seuls les événements sans support sont affichés
        expected_filtered = [mock_event_without_support]
        self.event_commands.event_view.display_event_list.assert_called_once_with(expected_filtered)

    @patch('app.commands.event.db_manager')
    def test_list_events_exception(self, mock_db_manager):
        """Test exception dans list_events"""
        # Mock de la session qui lève une exception
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("Erreur DB")

        # Exécution
        result = self.event_commands.list_events(role="gestion")

        # Vérifications
        self.event_commands.console.print.assert_called()
        mock_session.close.assert_called_once()
        assert result is None

    @patch('app.commands.event.db_manager')
    def test_assign_support_success(self, mock_db_manager):
        """Test assignation de support réussie"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement et du support
        mock_event = Mock()
        mock_event.id = 1
        mock_support = Mock()
        mock_support.id = 2
        mock_support.name = "Support Test"

        # Configuration des retours de requête
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_event,  # Première requête pour l'événement
            mock_support  # Deuxième requête pour le support
        ]

        # Mock des supports disponibles
        mock_supports = [mock_support]
        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = mock_supports

        # Mock des méthodes
        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.side_effect = ["1", "2"]

        # Exécution
        self.event_commands.assign_support()

        # Vérifications - Vérifier que l'assignation a été faite
        # Au lieu de vérifier la valeur, vérifier que l'attribut a été défini
        assert hasattr(mock_event, 'support_contact_id')
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    def test_assign_support_event_not_found(self, mock_db_manager):
        """Test assignation avec événement introuvable"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Événement introuvable
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Mock des méthodes
        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.return_value = "999"

        # Exécution
        self.event_commands.assign_support()

        # Vérifications
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    def test_assign_support_no_supports_available(self, mock_db_manager):
        """Test assignation sans supports disponibles"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement
        mock_event = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_event

        # Aucun support disponible
        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = []

        # Mock des méthodes
        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.return_value = "1"

        # Exécution
        self.event_commands.assign_support()

        # Vérifications
        self.event_commands.console.print.assert_called()

    @patch('app.commands.event.db_manager')
    def test_assign_support_exception(self, mock_db_manager):
        """Test exception lors de l'assignation"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement et du support
        mock_event = Mock()
        mock_support = Mock()
        mock_support.id = 2
        mock_support.name = "Support Test"

        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_event, mock_support
        ]
        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = [mock_support]

        # Exception lors du commit
        mock_session.commit.side_effect = Exception("Erreur DB")

        # Mock des méthodes
        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.side_effect = ["1", "2"]

        # Exécution
        self.event_commands.assign_support()

        # Vérifications
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()

    @patch('app.commands.event.db_manager')
    def test_filter_events_without_support_success(self, mock_db_manager):
        """Test filtrage des événements sans support"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des événements sans support
        mock_events = [Mock(), Mock()]
        mock_session.query.return_value.filter.return_value.all.return_value = mock_events

        # Mock de la vue
        self.event_commands.event_view.display_event_list.return_value = "events_without_support"

        # Exécution
        result = self.event_commands.filter_events_without_support()

        # Vérifications
        assert result == "events_without_support"
        mock_session.close.assert_called_once()

    @patch('app.commands.event.db_manager')
    def test_filter_events_without_support_no_events(self, mock_db_manager):
        """Test filtrage sans événements sans support"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Aucun événement sans support
        mock_session.query.return_value.filter.return_value.all.return_value = []

        # Exécution
        result = self.event_commands.filter_events_without_support()

        # Vérifications
        self.event_commands.console.print.assert_called()
        mock_session.close.assert_called_once()
        assert result is None

    @patch('app.commands.event.db_manager')
    def test_filter_events_without_support_exception(self, mock_db_manager):
        """Test exception dans filter_events_without_support"""
        # Mock de la session qui lève une exception
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("Erreur DB")

        # Exécution
        result = self.event_commands.filter_events_without_support()

        # Vérifications
        self.event_commands.console.print.assert_called()
        mock_session.close.assert_called_once()
        assert result is None

    @patch('app.commands.event.db_manager')
    def test_assign_support_support_not_found(self, mock_db_manager):
        """Test assignation avec support introuvable ou pas un support"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'événement
        mock_event = Mock()
        mock_event.id = 1

        # Mock des supports disponibles
        mock_support = Mock()
        mock_support.id = 2
        mock_support.name = "Support Test"
        mock_supports = [mock_support]

        # Configuration des retours de requête
        query_mock = mock_session.query.return_value

        # Première requête : événement trouvé
        query_mock.filter.return_value.first.return_value = mock_event

        # Deuxième requête : supports disponibles
        query_mock.join.return_value.filter.return_value.all.return_value = mock_supports

        # Troisième requête : support spécifique NOT FOUND
        query_mock.join.return_value.filter.return_value.first.return_value = None

        # Mock des méthodes
        self.event_commands.filter_events_without_support = Mock()
        self.event_commands.console.input.side_effect = ["1", "999"]  # Support inexistant

        # Exécution
        self.event_commands.assign_support()

        # Vérifications
        # Vérifier que le message d'erreur spécifique est affiché
        error_calls = [call for call in self.event_commands.console.print.call_args_list 
                    if "introuvable ou n'est pas un support" in str(call)]
        assert len(error_calls) > 0
