import pytest
from app.models.department import Department


def test_create_department_success(test_db):
    """Creation d'un département valide"""
    department = Department.create(
        name="commercial",
        description="Équipe commerciale"
    )
    assert department.name == "commercial"
    assert department.id is not None


def test_create_department_duplicate_name(test_db):
    """Création d'un département avec un nom déjà existant"""
    Department.create(name="support", description="Équipe support")
    with pytest.raises(Exception):
        Department.create(name="support", description="Autre description")


def test_create_department_empty_name(test_db):
    """Création d'un département avec un nom vide"""
    with pytest.raises(ValueError) as exc_info:
        Department.create(name="", description="Test")

    assert "Nom de département invalide" in str(exc_info.value)


def test_create_department_missing_name(test_db):
    """Création d'un département sans le nom"""
    with pytest.raises(ValueError) as exc_info:
        Department.create(description="Test sans nom")

    assert "Le nom du département est obligatoire" in str(exc_info.value)


def test_get_department_with_existing_id(test_db):
    # Maintenant vous pouvez créer sans conflit
    _dept = Department.create(name="gestion", description="Test")

    result = Department.get_department_with_id(_dept.id)
    assert result == "gestion"


def test_get_department_with_nonexistent_id():
    result = Department.get_department_with_id(99999)  # ID qui n'existe pas

    assert result is None


def test_get_department_with_none_id():
    result = Department.get_department_with_id(None)

    assert result is None
