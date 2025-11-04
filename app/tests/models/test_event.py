import pytest
from datetime import datetime, timezone, timedelta

from app.models.event import Event
from app.models.contract import Contract
from app.models.client import Client
from app.models.user import User
from app.models.department import Department


def test_create_event_success(test_db):
    """Test création d'événement réussie sans support"""
    dept = Department.create(name="commercial", description="Commercial")
    commercial = User.create(
        name="Commercial Test",
        mail="commercial@test.com",
        username="commercial",
        password="password123",
        department="commercial"
    )
    client = Client.create(
        name="Client Test",
        mail="client@test.com",
        phone="+33123456789",
        company_name="Test Company",
        commercial_contact_id=commercial.id,
        role="commercial"
    )
    contract = Contract.create(
        client_id=client.id,
        commercial_contact_id=commercial.id,
        total_amount=1000.0,
        remaining_amount=500.0,
        is_signed=True
    )
    
    date_start = datetime.now(timezone.utc) + timedelta(days=30)
    date_end = date_start + timedelta(hours=5)
    
    event = Event.create(
        name="Test Event",
        contract_id=contract.id,
        date_start=date_start,
        date_end=date_end,
        location="Paris",
        attendees=50
    )
    
    assert event.name == "Test Event"
    assert event.support_contact_id is None


def test_create_event_invalid_contract(test_db):
    """Test avec contrat inexistant"""
    date_start = datetime.now(timezone.utc) + timedelta(days=30)
    date_end = date_start + timedelta(hours=5)
    
    with pytest.raises(ValueError) as exc_info:
        Event.create(
            name="Test Event",
            contract_id=999,
            date_start=date_start,
            date_end=date_end,
            location="Paris",
            attendees=50
        )
    
    assert "Contrat avec l'ID 999 introuvable" in str(exc_info.value)


def test_create_event_invalid_support(test_db):
    """Test avec support inexistant"""
    dept = Department.create(name="commercial", description="Commercial")
    commercial = User.create(
        name="Commercial Test",
        mail="commercial@test.com",
        username="commercial",
        password="password123",
        department="commercial"
    )
    client = Client.create(
        name="Client Test",
        mail="client@test.com",
        phone="+33123456789",
        company_name="Test Company",
        commercial_contact_id=commercial.id,
        role="commercial"
    )
    contract = Contract.create(
        client_id=client.id,
        commercial_contact_id=commercial.id,
        total_amount=1000.0,
        remaining_amount=500.0,
        is_signed=True
    )
    
    date_start = datetime.now(timezone.utc) + timedelta(days=30)
    date_end = date_start + timedelta(hours=5)
    
    with pytest.raises(ValueError) as exc_info:
        Event.create(
            name="Test Event",
            contract_id=contract.id,
            date_start=date_start,
            date_end=date_end,
            location="Paris",
            attendees=50,
            support_contact_id=999
        )
    
    assert "Support avec l'ID 999 introuvable" in str(exc_info.value)
