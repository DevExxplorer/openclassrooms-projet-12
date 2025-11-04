import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.views.event import EventView


class TestEventView:
    
    def setup_method(self):
        self.event_view = EventView(contract_id=1)
        self.event_view.console = Mock()

    @patch('app.views.event.Prompt')
    def test_get_event_creation_form_success(self, mock_prompt):
        """Test formulaire création événement réussi"""
        mock_prompt.ask.side_effect = [
            "Test Event",
            "01-01-2024 10:00",
            "01-01-2024 18:00", 
            "Paris",
            "50",
            "Notes test"
        ]
        
        result = self.event_view.get_event_creation_form()
        
        assert result['name'] == "Test Event"
        assert result['contract_id'] == 1

    @patch('app.views.event.Prompt')
    def test_get_event_creation_form_invalid_date(self, mock_prompt):
        """Test formulaire création avec date invalide"""
        mock_prompt.ask.side_effect = [
            "Test Event",
            "invalid date",
            "01-01-2024 18:00",
            "Paris", 
            "50",
            "Notes"
        ]
        
        result = self.event_view.get_event_creation_form()
        assert result is None

    def test_display_event_list_empty(self):
        """Test affichage événements vide"""
        self.event_view.display_event_list([])
        self.event_view.console.print.assert_called()

    def test_display_event_list_with_support(self):
        """Test affichage événements avec support"""
        mock_event = Mock()
        mock_event.id = 1
        mock_event.name = "Test Event"
        mock_event.contract_id = 1
        mock_event.date_start.strftime.return_value = "01-01-2024 10:00"
        mock_event.date_end.strftime.return_value = "01-01-2024 18:00"
        mock_event.location = "Paris"
        mock_event.attendees = 50
        mock_event.notes = "Notes"
        mock_event.support_contact = Mock()
        mock_event.support_contact.name = "Support Test"
        
        self.event_view.display_event_list([mock_event])
        self.event_view.console.print.assert_called()

    def test_display_event_list_without_support(self):
        """Test affichage événements sans support"""
        mock_event = Mock()
        mock_event.id = 1
        mock_event.name = "Test Event"
        mock_event.contract_id = 1
        mock_event.date_start.strftime.return_value = "01-01-2024 10:00"
        mock_event.date_end.strftime.return_value = "01-01-2024 18:00"
        mock_event.location = "Paris"
        mock_event.attendees = 50
        mock_event.notes = None  # ← Test notes vides
        mock_event.support_contact = None  # ← Test sans support
        
        self.event_view.display_event_list([mock_event])
        self.event_view.console.print.assert_called()

    @patch('app.views.event.Prompt')
    def test_get_event_update_form_success(self, mock_prompt):
        """Test formulaire mise à jour réussi"""
        mock_event = Mock()
        mock_event.name = "Old Event"
        mock_event.date_start.strftime.return_value = "01-01-2024 10:00"
        mock_event.date_end.strftime.return_value = "01-01-2024 18:00"
        mock_event.location = "Paris"
        mock_event.attendees = 50
        mock_event.notes = "Notes"
        
        mock_prompt.ask.side_effect = [
            "New Event",
            "02-01-2024 10:00",
            "02-01-2024 18:00",
            "Lyon",
            "100", 
            "New notes"
        ]
        
        result = self.event_view.get_event_update_form(mock_event)
        assert result['name'] == "New Event"

    @patch('app.views.event.Prompt')
    def test_get_event_update_form_invalid_date(self, mock_prompt):
        """Test mise à jour avec date invalide"""
        mock_event = Mock()
        mock_event.name = "Event"
        mock_event.date_start.strftime.return_value = "01-01-2024 10:00"
        mock_event.date_end.strftime.return_value = "01-01-2024 18:00"
        mock_event.location = "Paris"
        mock_event.attendees = 50
        mock_event.notes = "Notes"
        
        mock_prompt.ask.side_effect = [
            "Event",
            "invalid date",  # Date début invalide
            "",
            "",
            "",
            ""
        ]
        
        result = self.event_view.get_event_update_form(mock_event)
        assert result is None

    def test_display_supports_available_empty(self):
        """Test affichage supports vide"""
        self.event_view.display_supports_available([])
        self.event_view.console.print.assert_called()

    def test_display_supports_available_with_data(self):
        """Test affichage supports avec données"""
        mock_support = Mock()
        mock_support.id = 1
        mock_support.name = "Support Test"
        
        self.event_view.display_supports_available([mock_support])
        self.event_view.console.print.assert_called()

    def test_parse_date_valid(self):
        """Test parse date valide"""
        result = self.event_view._parse_date("01-01-2024 10:00")
        assert result == datetime(2024, 1, 1, 10, 0)

    def test_parse_date_invalid(self):
        """Test parse date invalide"""
        result = self.event_view._parse_date("invalid")
        assert result is None

    def test_parse_date_empty(self):
        """Test parse date vide"""
        result = self.event_view._parse_date("")
        assert result is None

    @patch('app.views.event.Prompt')
    def test_get_event_update_form_invalid_end_date(self, mock_prompt):
        """Test mise à jour avec date de fin invalide"""
        mock_event = Mock()
        mock_event.name = "Event"
        mock_event.date_start.strftime.return_value = "01-01-2024 10:00"
        mock_event.date_end.strftime.return_value = "01-01-2024 18:00"
        mock_event.location = "Paris"
        mock_event.attendees = 50
        mock_event.notes = "Notes"
        
        mock_prompt.ask.side_effect = [
            "Event",
            "01-01-2024 10:00",  # Date début valide
            "invalid end date",  # Date fin invalide
            "",
            "",
            ""
        ]
        
        result = self.event_view.get_event_update_form(mock_event)
        assert result is None