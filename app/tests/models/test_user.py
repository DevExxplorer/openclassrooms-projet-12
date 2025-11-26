import pytest # noqa
from app.models.user import User
from app.models.department import Department


def test_hash_password():
    """Test que le mot de passe est bien haché"""
    password = "monMotDePasse123!"

    hashed = User.hash_password(password)

    # Le hash ne doit pas être égal au mot de passe original
    assert hashed != password

    # Le hash doit être une chaîne non vide
    assert isinstance(hashed, str)
    assert len(hashed) > 0

    # Le hash doit commencer par $argon2 (signature Argon2)
    assert hashed.startswith("$argon2")


def test_hash_password_different_salts():
    """Test que deux hachages du même mot de passe donnent des résultats différents (salt)"""
    password = "testPassword"

    hash1 = User.hash_password(password)
    hash2 = User.hash_password(password)

    # Les deux hashs doivent être différents (différents salts)
    assert hash1 != hash2


def test_hash_empty_password():
    """Test hachage d'un mot de passe vide"""
    hash_empty = User.hash_password("")

    assert isinstance(hash_empty, str)
    assert len(hash_empty) > 0


def test_verify_password_correct():
    """Test vérification d'un mot de passe correct"""
    user = User()
    password = "testPassword123"
    user.password_hash = User.hash_password(password)

    # Le mot de passe correct doit être vérifié
    assert user.verify_password(password) is True


def test_verify_password_incorrect():
    """Test vérification d'un mot de passe incorrect"""
    user = User()
    user.password_hash = User.hash_password("correctPassword")

    # Un mauvais mot de passe doit être rejeté
    assert user.verify_password("wrongPassword") is False

# Tests authenticate method


def test_authenticate_success(test_db):
    """Test authentification réussie avec identifiants corrects"""
    # Créer un département
    _dept = Department.create(name="commercial", description="Équipe commerciale")

    # Créer un utilisateur
    _user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="motdepasse123",
        department="commercial"
    )

    # Test d'authentification
    authenticated_user = User.authenticate("jean.test", "motdepasse123")

    assert authenticated_user is not None
    assert authenticated_user.username == "jean.test"
    assert authenticated_user.name == "Jean Test"


def test_authenticate_wrong_password(test_db):
    """Test authentification qui échoue avec mauvais mot de passe"""

    # Création  du département et de l'utilisateur
    dept = Department.create(name="support", description="Équipe support")
    user = User.create(
        employee_number="EMP002",
        name="Marie Test",
        mail="marie@test.com",
        username="marie.test",
        password="bonMotDePasse",
        department="support"
    )

    # Tenter authentification avec le mauvais mot de passe
    authenticated_user = User.authenticate("marie.test", "mauvaisMotDePasse")

    assert authenticated_user is None


def test_authenticate_wrong_username(test_db):
    """Test authentification qui échoue avec le mauvais nom d'utilisateur"""

    # Création du département et de l'utilisateur
    dept = Department.create(name="gestion", description="Équipe gestion")
    user = User.create(
        employee_number="EMP003",
        name="Paul Test",
        mail="paul@test.com",
        username="paul.test",
        password="password123",
        department="gestion"
    )

    # Tenter authentification avec mauvais username
    authenticated_user = User.authenticate("utilisateurInexistant", "password123")

    assert authenticated_user is None


def test_authenticate_user_not_exists(test_db):
    """Test authentification avec utilisateur qui n'existe pas"""
    authenticated_user = User.authenticate("inexistant", "password")

    assert authenticated_user is None


def test_authenticate_empty_credentials(test_db):
    """Test authentification avec identifiants vides"""
    authenticated_user = User.authenticate("", "")

    assert authenticated_user is None


# Tests create method
def test_create_user_success(test_db):
    """Création d'utilisateur réussie"""
    dept = Department.create(name="commercial", description="Équipe commerciale")

    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="password123",
        department="commercial"
    )

    assert user.name == "Jean Test"
    assert user.mail == "jean@test.com"
    assert user.username == "jean.test"
    assert user.department_id == dept.id
    assert user.password_hash != "password123"


def test_create_user_missing_password(test_db):
    """Création sans mot de passe"""
    dept = Department.create(name="support", description="Équipe support")

    with pytest.raises(ValueError) as exc_info:
        User.create(
            employee_number="EMP002",
            name="Test User",
            mail="test@test.com",
            username="test",
            department="support"
        )

    assert "Le mot de passe est obligatoire" in str(exc_info.value)


def test_create_user_invalid_department(test_db):
    """Création avec département inexistant"""
    with pytest.raises(ValueError) as exc_info:
        User.create(
            employee_number="EMP003",
            name="Test User",
            mail="test@test.com",
            username="test",
            password="password123",
            department="inexistant"
        )

    assert "Département 'inexistant' introuvable" in str(exc_info.value)


# Tests update method
def test_update_user_success(test_db):
    """Mise à jour réussie par méthode d'instance"""
    dept1 = Department.create(name="commercial", description="Commercial")
    dept2 = Department.create(name="support", description="Support")

    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="password123",
        department="commercial"
    )

    # ✅ Méthode d'instance
    user.update(name="Jean Modifié", department="support")

    assert user.name == "Jean Modifié"
    # Rechargez depuis la DB pour vérifier
    updated_user = User.get_by_id(user.id)
    assert updated_user.name == "Jean Modifié"


def test_update_user_invalid_department(test_db):
    """Mise à jour avec département inexistant"""
    dept = Department.create(name="commercial", description="Commercial")

    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="password123",
        department="commercial"
    )

    with pytest.raises(ValueError) as exc_info:
        user.update(department="departement_inexistant")

    assert "Département 'departement_inexistant' introuvable" in str(exc_info.value)


def test_update_user_with_password(test_db):
    """Mise à jour avec nouveau mot de passe"""
    dept = Department.create(name="commercial", description="Commercial")

    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="ancienMotDePasse",
        department="commercial"
    )

    old_password_hash = user.password_hash

    user.update(password="nouveauMotDePasse123")

    # Recharger depuis la DB
    updated_user = User.get_by_id(user.id)

    assert updated_user.password_hash != old_password_hash
    assert not updated_user.verify_password("ancienMotDePasse")
    assert updated_user.verify_password("nouveauMotDePasse123")


def test_update_user_with_empty_password(test_db):
    """Mise à jour avec mot de passe vide (ne doit pas changer)"""
    dept = Department.create(name="commercial", description="Commercial")

    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="ancienMotDePasse",
        department="commercial"
    )

    old_password_hash = user.password_hash

    # Mot de passe vide ne doit pas changer le hash
    user.update(password="   ", name="Nouveau nom")

    updated_user = User.get_by_id(user.id)

    assert updated_user.password_hash == old_password_hash
    assert updated_user.verify_password("ancienMotDePasse")
    assert updated_user.name == "Nouveau nom"


# Tests Delete method
def test_delete_user_success(test_db):
    """Suppression réussie par équipe gestion"""
    dept = Department.create(name="commercial", description="Commercial")
    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="password123",
        department="commercial"
    )

    result = User.delete(user_id=user.id, role="gestion")

    assert result is True

    # Vérifier que l'utilisateur n'existe plus
    deleted_user = User.get_by_id(user.id)
    assert deleted_user is None


def test_delete_user_wrong_role(test_db):
    """Suppression refusée pour mauvais rôle"""
    dept = Department.create(name="commercial", description="Commercial")
    user = User.create(
        employee_number="EMP001",
        name="Jean Test",
        mail="jean@test.com",
        username="jean.test",
        password="password123",
        department="commercial"
    )

    with pytest.raises(PermissionError) as exc_info:
        User.delete(user_id=user.id, role="commercial")

    assert "Seule l'équipe gestion peut supprimer" in str(exc_info.value)


def test_delete_user_not_found(test_db):
    """Suppression d'utilisateur inexistant"""
    with pytest.raises(ValueError) as exc_info:
        User.delete(user_id=999, role="gestion")

    assert "Utilisateur avec l'ID 999 introuvable" in str(exc_info.value)


# Tests Get_all method
def test_get_all_users_empty(test_db):
    """Test si aucun utilisateur"""
    users = User.get_all()
    assert len(users) == 0


def test_get_all_users_with_data(test_db):
    """Test avec données valide"""
    dept = Department.create(name="commercial", description="Commercial")

    User.create(
        employee_number="EMP001",
        name="User 1",
        mail="user1@test.com",
        username="user1",
        password="password123",
        department="commercial"
    )

    User.create(
        employee_number="EMP002",
        name="User 2",
        mail="user2@test.com",
        username="user2",
        password="password123",
        department="commercial"
    )

    users = User.get_all()

    assert len(users) == 2
    assert users[0].name == "User 1"
    assert users[1].name == "User 2"


# Test department
def test_department_name_with_department():
    user = User()
    user.department = Department()
    user.department.name = "gestion"

    assert user.department_name == "gestion"


def test_department_name_without_department():
    user = User()
    user.department = None
    assert user.department_name is None


def test_create_user_auto_employee_number(test_db):
    """Test création sans employee_number (auto-généré)"""
    dept = Department.create(name="commercial", description="Commercial")

    user = User.create(
        name="Test Auto",
        mail="auto@test.com",
        username="auto.test",
        password="password123",
        department="commercial"
    )

    assert user.employee_number.startswith("EMP")
    assert len(user.employee_number) == 7


def test_get_by_id_not_found(test_db):
    """Test get_by_id avec ID inexistant"""
    user = User.get_by_id(999)
    assert user is None


def test_get_by_id_user_without_department(test_db):
    """Test get_by_id avec utilisateur sans département"""
    # Créer un utilisateur directement sans département pour ce test spécial
    from app.database.db import db_manager

    session = db_manager.get_session()
    try:
        user = User(
            employee_number="EMP999",
            name="Test Sans Dept",
            mail="sansdept@test.com",
            username="sans.dept",
            password_hash=User.hash_password("password123")
            # Pas de department_id - il sera None
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        user_id = user.id
    finally:
        session.close()

    # Tester get_by_id avec cet utilisateur sans département
    retrieved_user = User.get_by_id(user_id)

    assert retrieved_user is not None
    assert retrieved_user.department is None
    assert retrieved_user.department_name is None


def test_get_by_department_success(test_db):
    """Test récupération par département"""
    dept1 = Department.create(name="commercial", description="Commercial")
    dept2 = Department.create(name="support", description="Support")

    User.create(
        name="Commercial 1",
        mail="comm1@test.com",
        username="comm1",
        password="password123",
        department="commercial"
    )

    User.create(
        name="Support 1",
        mail="support1@test.com",
        username="support1",
        password="password123",
        department="support"
    )

    commercial_users = User.get_by_department("commercial")
    support_users = User.get_by_department("support")

    assert len(commercial_users) == 1
    assert len(support_users) == 1
    assert commercial_users[0].name == "Commercial 1"
    assert support_users[0].name == "Support 1"
