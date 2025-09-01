import pytest
from app.models import Client

VALID_ROLES = ["commercial"]
INVALID_ROLES = [
    "support",
    "gestion",
    "admin",
    "",
    None,
    "COMMERCIAL",
    "Commercial",
    "random_role"
]
VALID_EMAILS = [
    "test@email.com",
    "user@gmail.com",
    "contact@company.fr"
]
INVALID_EMAILS = [
    "invalid-email",
    "@gmail.com",
    "test@"
]
VALID_PHONES = [
    "+12345678912",
    "+000000000000000",
]
INVALID_PHONES = [
    "123+",
    "12345667776+",
    "+1234",
    "0000+12344",
    "None"
]

# TEST CREATE METHODS

# TEST ROLE
@pytest.mark.parametrize("role", VALID_ROLES)
def test_create_valid_roles(role, test_db):
    """Test que le rôle 'commercial' peut créer des clients"""
    client = Client.create(
        role=role,
        name="Jean Dupont",
        mail="jean@test.com"
    )
    assert client.name == "Jean Dupont"
    assert client.mail == "jean@test.com"

@pytest.mark.parametrize("role", INVALID_ROLES)
def test_create_invalid_roles(role, test_db):
    """Test que tous les autres rôles sont rejetés"""
    with pytest.raises(PermissionError) :
        Client.create(
            role=role,
            name="Jean Dupont",
            mail="jean@test.com"
        )

# TEST NAME
def test_create_client_empty_name(test_db):
    """Test : nom vide échoue"""
    with pytest.raises(ValueError):
        Client.create(
            role="commercial",
            name="",
            mail="test@email.com"
        )
    assert "Le nom du client est obligatoire"

def test_create_client_whitespace_name(test_db):
    """Test : nom avec espaces uniquement échoue"""
    with pytest.raises(ValueError) :
        Client.create(
            role="commercial",
            name="   ",
            mail="test@email.com"
        )
    assert "Le nom du client est obligatoire"

# TEST EMAILS

@pytest.mark.parametrize("email", VALID_EMAILS)
def test_create_valid_emails(email, test_db):
    """Test : email valide"""
    client = Client.create(
        role="commercial",
        name="Jean",
        mail=email
    )
    assert client.mail == email

@pytest.mark.parametrize("email", INVALID_EMAILS)
def test_create_invalid_emails(email, test_db):
    """Test : email invalide"""
    with pytest.raises(ValueError):
        Client.create(
            role="commercial",
            name="Pierre",
            mail=email
        )

def test_create_client_duplicate_email(test_db):
    """Test : email déjà existant échoue"""
    # Création d'un premier client
    Client.create(
        role="commercial",
        name="Premier Client",
        mail="duplicate@test.com"
    )

    # Tenter de créer un second avec le même email
    with pytest.raises(ValueError):
        Client.create(
            role="commercial",
            name="Second Client",
            mail="duplicate@test.com"
        )
    assert "Le client avec l'email 'duplicate@test.com' existe déjà"

# TEST PHONES
@pytest.mark.parametrize("phone", VALID_PHONES)
def test_create_valid_phones(phone, test_db):
    """Test : tel valide"""
    client = Client.create(
        role="commercial",
        name="Jacques",
        phone=phone,
        mail = "test@email.com"
    )
    assert client.phone == phone

@pytest.mark.parametrize("phone", INVALID_PHONES)
def test_create_invalid_phones(phone, test_db):
    """Test : tel invalide"""
    with pytest.raises(ValueError):
        Client.create(
            role="commercial",
            name="Philippe",
            phone=phone,
            mail="test@email.com"
        )


# TEST READ METHODS

def test_get_all_clients(test_db):
    """Test : récupérer tous les clients"""
    # Créer quelques clients
    Client.create(role="commercial", name="Client1", mail="client1@test.com")
    Client.create(role="commercial", name="Client2", mail="client2@test.com")

    # Récupérer tous les clients
    clients = Client.get_all()

    assert len(clients) == 2
    assert clients[0].name == "Client1"
    assert clients[1].name == "Client2"

def test_get_all_clients_empty(test_db):
    """Test : récupérer tous les clients quand la table est vide"""
    clients = Client.get_all()
    assert len(clients) == 0

def test_get_by_id_success(test_db):
    """Test : récupérer un client par ID existant"""
    created_client = Client.create(role="commercial", name="Jean", mail="jean@test.com")

    found_client = Client.get_by_id(created_client.id)

    assert found_client.id == created_client.id
    assert found_client.name == "Jean"
    assert found_client.mail == "jean@test.com"

def test_get_by_id_not_found(test_db):
    """Test : récupérer un client par ID inexistant"""
    with pytest.raises(ValueError) as exc_info:
        Client.get_by_id(999)

    assert "Client avec l'ID 999 introuvable" in str(exc_info.value)

def test_get_by_email_success(test_db):
    """Test : récupérer un client par email existant"""
    Client.create(role="commercial", name="Marie", mail="marie@test.com")

    found_client = Client.get_by_email("marie@test.com")

    assert found_client.name == "Marie"
    assert found_client.mail == "marie@test.com"

def test_get_by_email_not_found(test_db):
    """Test : récupérer un client par email inexistant"""
    with pytest.raises(ValueError) as exc_info:
        Client.get_by_email("inexistant@test.com")

    assert "Client avec l'email 'inexistant@test.com' introuvable" in str(exc_info.value)