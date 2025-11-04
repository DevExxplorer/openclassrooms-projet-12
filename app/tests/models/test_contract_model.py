import pytest

from app.models.contract import Contract
from app.models.client import Client
from app.models.user import User
from app.models.department import Department


def test_create_contract_success(test_db):
    """Test création de contrat réussie"""
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
        status="signé"
    )

    assert contract.client_id == client.id
    assert contract.commercial_contact_id == commercial.id
    assert contract.total_amount == 1000.0
    assert contract.remaining_amount == 500.0
    assert contract.is_signed is True


def test_create_contract_not_signed(test_db):
    """Test création de contrat non signé"""
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
        total_amount=2000.0,
        remaining_amount=2000.0,
        status="non signé"
    )

    assert contract.is_signed is False


def test_create_contract_invalid_client(test_db):
    """Test création avec client inexistant"""
    dept = Department.create(name="commercial", description="Commercial")

    commercial = User.create(
        name="Commercial Test",
        mail="commercial@test.com",
        username="commercial",
        password="password123",
        department="commercial"
    )

    with pytest.raises(ValueError) as exc_info:
        Contract.create(
            client_id=999,
            commercial_contact_id=commercial.id,
            total_amount=1000.0,
            remaining_amount=500.0,
            status="signé"
        )

    assert "Client avec l'ID 999 introuvable" in str(exc_info.value)


def test_create_contract_invalid_commercial(test_db):
    """Test création avec commercial inexistant"""
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

    with pytest.raises(ValueError) as exc_info:
        Contract.create(
            client_id=client.id,
            commercial_contact_id=999,
            total_amount=1000.0,
            remaining_amount=500.0,
            status="signé"
        )

    assert "Commercial avec l'ID 999 introuvable" in str(exc_info.value)
