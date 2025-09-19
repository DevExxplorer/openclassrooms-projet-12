import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.db import DatabaseManager, Base


class TestDatabaseManager:
    
    @patch('app.database.db.os.getenv')
    @patch('app.database.db.create_engine')
    @patch('app.database.db.sessionmaker')
    def test_init_with_default_port(self, mock_sessionmaker, mock_create_engine, mock_getenv):
        """Test l'initialisation avec le port par défaut (ligne 31)"""
        # Simuler les variables d'environnement sans DB_PORT
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_HOST': 'localhost',
            'DB_NAME': 'testdb',
            'MODE': 'prod'
        }.get(key, default)
        
        db_manager = DatabaseManager()
        
        # Vérifier que l'URL contient le port par défaut 5432
        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        mock_create_engine.assert_called_once_with(expected_url, echo=False)

    @patch('app.database.db.os.getenv')
    @patch('app.database.db.create_engine')
    @patch('app.database.db.sessionmaker')
    def test_init_dev_mode(self, mock_sessionmaker, mock_create_engine, mock_getenv):
        """Test l'initialisation en mode dev (ligne 32)"""
        mock_getenv.side_effect = lambda key, default=None: {
            'DB_USER': 'testuser',
            'DB_PASSWORD': 'testpass',
            'DB_HOST': 'localhost',
            'DB_PORT': '5432',
            'DB_NAME': 'testdb',
            'MODE': 'dev'  # Mode dev pour echo=True
        }.get(key, default)
        
        db_manager = DatabaseManager()
        
        # Vérifier que echo=True en mode dev
        expected_url = "postgresql://testuser:testpass@localhost:5432/testdb"
        mock_create_engine.assert_called_once_with(expected_url, echo=True)

    @patch('app.database.db.inspect')
    def test_tables_exist_missing_tables(self, mock_inspect):
        """Test tables_exist quand des tables sont manquantes (lignes 44-45)"""
        # Mock de l'inspector
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['existing_table']
        mock_inspect.return_value = mock_inspector
        
        # Mock des tables attendues
        with patch.object(Base.metadata, 'tables', {'expected_table1': Mock(), 'expected_table2': Mock()}):
            db_manager = DatabaseManager()
            result = db_manager.tables_exist()
            
            assert result is False

    @patch('app.database.db.inspect')
    def test_tables_exist_all_tables_present(self, mock_inspect):
        """Test tables_exist quand toutes les tables existent"""
        # Mock de l'inspector
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['table1', 'table2']
        mock_inspect.return_value = mock_inspector
        
        # Mock des tables attendues
        with patch.object(Base.metadata, 'tables', {'table1': Mock(), 'table2': Mock()}):
            db_manager = DatabaseManager()
            result = db_manager.tables_exist()
            
            assert result is True

    @patch('builtins.print')
    @patch.object(Base.metadata, 'create_all')
    def test_create_tables(self, mock_create_all, mock_print):
        """Test create_tables (ligne 51)"""
        db_manager = DatabaseManager()
        db_manager.create_tables()
        
        mock_create_all.assert_called_once_with(bind=db_manager.engine)
        mock_print.assert_called_once_with("Tables créées avec succès !")

    def test_get_session(self):
        """Test get_session (ligne 57)"""
        db_manager = DatabaseManager()
        
        # Mock de SessionLocal pour retourner une session mock
        mock_session = Mock()
        db_manager.SessionLocal = Mock(return_value=mock_session)
        
        result = db_manager.get_session()
        
        db_manager.SessionLocal.assert_called_once()
        assert result == mock_session

    @patch('builtins.print')
    @patch.object(Base.metadata, 'drop_all')
    def test_drop_tables(self, mock_drop_all, mock_print):
        """Test drop_tables (ligne 58)"""
        db_manager = DatabaseManager()
        db_manager.drop_tables()
        
        mock_drop_all.assert_called_once_with(bind=db_manager.engine)
        mock_print.assert_called_once_with("Tables supprimées !")