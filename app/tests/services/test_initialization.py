import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.initialization import Initialization


class TestInitialization:
    """Tests pour Initialization"""

    @patch('app.services.initialization.Department')
    @patch('app.services.initialization.db_manager')
    def test_initialize_departments_new_departments(self, mock_db_manager, mock_department):
        """Test initialisation avec nouveaux départements"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des départements à créer
        mock_department.DEPARTMENTS = ['commercial', 'support', 'gestion']

        # Mock qu'aucun département n'existe
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Mock de la création de département
        mock_dept = Mock()
        mock_dept.name = 'commercial'
        mock_department.create.return_value = mock_dept

        # Exécution
        results = Initialization.initialize_departments()

        # Vérifications
        assert len(results) == 3
        # Vérifier que tous les départements ont été créés (True)
        for dept, created in results:
            assert created is True

        # Vérifier que create a été appelé 3 fois
        assert mock_department.create.call_count == 3
        # Vérifier que la session a été fermée 3 fois
        assert mock_session.close.call_count == 3

    @patch('app.services.initialization.Department')
    @patch('app.services.initialization.db_manager')
    def test_initialize_departments_existing_departments(self, mock_db_manager, mock_department):
        """Test initialisation avec départements existants"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des départements
        mock_department.DEPARTMENTS = ['commercial', 'support']

        # Mock que les départements existent déjà
        mock_existing_dept = Mock()
        mock_existing_dept.name = 'commercial'
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_dept

        # Exécution
        results = Initialization.initialize_departments()

        # Vérifications
        assert len(results) == 2
        # Vérifier qu'aucun département n'a été créé (False)
        for dept, created in results:
            assert created is False
            assert dept == mock_existing_dept

        # Vérifier que create n'a pas été appelé
        mock_department.create.assert_not_called()

    @patch('app.services.initialization.Department')
    @patch('app.services.initialization.db_manager')
    def test_initialize_departments_mixed_scenario(self, mock_db_manager, mock_department):
        """Test initialisation avec départements mixtes (certains existent, d'autres non)"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des départements
        mock_department.DEPARTMENTS = ['commercial', 'support']

        # Mock : premier département existe, deuxième n'existe pas
        mock_existing_dept = Mock()
        mock_new_dept = Mock()
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_existing_dept,  # commercial existe
            None                 # support n'existe pas
        ]
        mock_department.create.return_value = mock_new_dept

        # Exécution
        results = Initialization.initialize_departments()

        # Vérifications
        assert len(results) == 2
        # Premier résultat : département existant
        assert results[0] == (mock_existing_dept, False)
        # Deuxième résultat : nouveau département
        assert results[1] == (mock_new_dept, True)

        # Vérifier que create a été appelé une fois
        mock_department.create.assert_called_once()

    @patch('app.services.initialization.Department')
    @patch('app.services.initialization.db_manager')
    def test_initialize_departments_exception(self, mock_db_manager, mock_department):
        """Test initialisation avec exception"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des départements
        mock_department.DEPARTMENTS = ['commercial']

        # Mock d'exception lors de la requête
        mock_session.query.side_effect = Exception("Erreur DB")

        # Exécution
        results = Initialization.initialize_departments()

        # Vérifications
        assert len(results) == 1
        dept, error = results[0]
        assert dept is None
        assert "Erreur pour commercial:" in error

    @patch('app.services.initialization.User')
    def test_create_default_admin_success(self, mock_user):
        """Test création d'admin par défaut réussie"""
        # Mock de l'admin créé
        mock_admin = Mock()
        mock_admin.name = "Admin"
        mock_user.create.return_value = mock_admin

        # Exécution
        admin, created = Initialization.create_default_admin()

        # Vérifications
        assert admin == mock_admin
        assert created is True
        mock_user.create.assert_called_once_with(
            name="Admin",
            mail="admin@epicevents.com",
            username="admin",
            password="admin123",
            department="gestion"
        )

    @patch('app.services.initialization.User')
    def test_create_default_admin_exception(self, mock_user):
        """Test création d'admin avec exception"""
        # Mock d'exception lors de la création
        mock_user.create.side_effect = Exception("Erreur création admin")

        # Exécution et vérification de l'exception
        with pytest.raises(Exception) as exc_info:
            Initialization.create_default_admin()

        assert "Erreur création admin" in str(exc_info.value)

    @patch('app.services.initialization.Initialization.initialize_departments')
    @patch('app.services.initialization.Initialization.create_default_admin')
    def test_initialize_application_success(self, mock_create_admin, mock_init_departments):
        """Test initialisation complète réussie"""
        # Mock des résultats
        mock_dept_results = [("dept1", True), ("dept2", False)]
        mock_init_departments.return_value = mock_dept_results

        mock_admin = Mock()
        mock_create_admin.return_value = (mock_admin, True)

        # Exécution
        results = Initialization.initialize_application()

        # Vérifications
        assert results['departments'] == mock_dept_results
        assert results['admin'] == (mock_admin, True)
        assert results['errors'] == []

        mock_init_departments.assert_called_once()
        mock_create_admin.assert_called_once()

    @patch('app.services.initialization.Initialization.initialize_departments')
    @patch('app.services.initialization.Initialization.create_default_admin')
    def test_initialize_application_exception(self, mock_create_admin, mock_init_departments):
        """Test initialisation complète avec exception"""
        # Mock des départements OK
        mock_dept_results = [("dept1", True)]
        mock_init_departments.return_value = mock_dept_results

        # Mock d'exception lors de la création admin
        mock_create_admin.side_effect = Exception("Erreur admin")

        # Exécution
        results = Initialization.initialize_application()

        # Vérifications
        assert results['departments'] == mock_dept_results
        assert results['admin'] is None
        assert len(results['errors']) == 1
        assert "Erreur lors de l'initialisation: Erreur admin" in results['errors'][0]

    @patch('app.services.initialization.Initialization.initialize_departments')
    def test_initialize_application_departments_exception(self, mock_init_departments):
        """Test initialisation avec exception dans les départements"""
        # Mock d'exception dans initialize_departments
        mock_init_departments.side_effect = Exception("Erreur départements")

        # Exécution
        results = Initialization.initialize_application()

        # Vérifications
        assert results['departments'] == []
        assert results['admin'] is None
        assert len(results['errors']) == 1
        assert "Erreur lors de l'initialisation: Erreur départements" in results['errors'][0]

    def test_initialize_application_structure(self):
        """Test structure du résultat d'initialize_application"""
        # Mock toutes les méthodes pour éviter les appels réels
        with patch('app.services.initialization.Initialization.initialize_departments') as mock_dept, \
            patch('app.services.initialization.Initialization.create_default_admin') as mock_admin:

            mock_dept.return_value = []
            mock_admin.return_value = (None, False)

            # Exécution
            results = Initialization.initialize_application()

            # Vérifications de la structure
            assert 'departments' in results
            assert 'admin' in results
            assert 'errors' in results
            assert isinstance(results['departments'], list)
            assert isinstance(results['errors'], list)

    @patch('app.services.initialization.Department')
    @patch('app.services.initialization.db_manager')
    def test_initialize_departments_empty_list(self, mock_db_manager, mock_department):
        """Test initialisation avec liste de départements vide"""
        # Mock des départements vides
        mock_department.DEPARTMENTS = []

        # Exécution
        results = Initialization.initialize_departments()

        # Vérifications
        assert results == []

    @patch('app.services.initialization.Department')
    @patch('app.services.initialization.db_manager')
    def test_initialize_departments_session_close_always_called(self, mock_db_manager, mock_department):
        """Test que session.close() est toujours appelé même en cas d'exception"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des départements
        mock_department.DEPARTMENTS = ['commercial']

        # Mock que le département n'existe pas
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Mock d'exception lors de la création (pas de la requête)
        mock_department.create.side_effect = Exception("Erreur création")

        # Exécution
        results = Initialization.initialize_departments()

        # Vérifications que close a été appelé malgré l'exception
        mock_session.close.assert_called_once()
        assert len(results) == 1
        assert results[0][0] is None
