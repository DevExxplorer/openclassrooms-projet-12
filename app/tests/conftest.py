import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.db import Base, db_manager


@pytest.fixture(scope="function")
def test_db():
    """Crée une base de données en mémoire pour chaque test"""
    # Base de données temporaire en mémoire
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)

    # Remplacer temporairement la session
    test_session = sessionmaker(bind=engine)

    # Monkey patch pour utiliser la DB de test
    original_get_session = db_manager.get_session
    db_manager.get_session = lambda: test_session()

    yield engine

    # Restaurer après le test
    db_manager.get_session = original_get_session