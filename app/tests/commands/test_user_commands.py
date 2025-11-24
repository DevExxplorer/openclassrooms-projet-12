import pytest # noqa
from unittest.mock import Mock, patch

from app.controllers.user import UserCommands


class TestUserCommands:
    """Tests pour UserCommands"""

    def setup_method(self):
        """Setup pour chaque test"""
        self.mock_user = Mock()
        self.mock_user.id = 1
        self.mock_user.name = "Test User"

        self.user_commands = UserCommands(current_user=self.mock_user)

        # Mock de la vue et console après création
        self.user_commands.user_view = Mock()
        self.user_commands.console = Mock()

    @patch('app.commands.user.User')
    def test_create_user_success(self, mock_user):
        """Test création d'utilisateur réussie"""
        # Mock de la vue
        self.user_commands.user_view.get_user_creation_form.return_value = {
            'name': 'Nouveau User',
            'mail': 'user@test.com',
            'username': 'new.user',
            'password': 'password123',
            'department': 'commercial'
        }

        # Mock de User.create
        mock_user_instance = Mock()
        mock_user_instance.name = "Nouveau User"
        mock_user.create.return_value = mock_user_instance

        # Exécution
        self.user_commands.create_user()

        # Vérifications
        mock_user.create.assert_called_once()
        self.user_commands.console.print.assert_called()

    @patch('app.commands.user.User')
    def test_create_user_exception(self, mock_user):
        """Test exception lors de la création d'utilisateur"""
        # Mock de la vue
        self.user_commands.user_view.get_user_creation_form.return_value = {
            'name': 'Nouveau User'
        }

        # Exception lors de la création
        mock_user.create.side_effect = Exception("Erreur création utilisateur")

        # Exécution
        self.user_commands.create_user()

        # Vérifications
        self.user_commands.console.print.assert_called()

    @patch('app.commands.user.Department')
    @patch('app.commands.user.User')
    @patch('app.commands.user.db_manager')
    def test_update_user_success(self, mock_db_manager, mock_user, mock_department):
        """Test mise à jour d'utilisateur réussie"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant avec département
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.name = "User Test"
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Mock des vues et méthodes
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'name': 'User Modifié',
            'mail': 'modified@test.com'
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        self.user_commands.console.print.assert_called()

    @patch('app.commands.user.db_manager')
    def test_update_user_not_found(self, mock_db_manager):
        """Test mise à jour avec utilisateur introuvable"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Utilisateur introuvable
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 999

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        self.user_commands.console.print.assert_called()
        mock_session.close.assert_called_once()

    @patch('app.commands.user.Department')
    @patch('app.commands.user.User')
    @patch('app.commands.user.db_manager')
    def test_update_user_with_department_change(self, mock_db_manager, mock_user, mock_department):
        """Test mise à jour avec changement de département"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.name = "User Test"
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"

        # Mock du nouveau département
        mock_new_dept = Mock()
        mock_new_dept.id = 2

        # Configuration des requêtes
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_existing_user,  # Première requête pour l'utilisateur
            mock_new_dept        # Deuxième requête pour le département
        ]

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'name': 'User Modifié',
            'department': 'support'  # Changement de département
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        assert mock_existing_user.department_id == 2
        mock_session.commit.assert_called_once()

    @patch('app.commands.user.Department')
    @patch('app.commands.user.User')
    @patch('app.commands.user.db_manager')
    def test_update_user_department_not_found(self, mock_db_manager, mock_user, mock_department):
        """Test mise à jour avec département introuvable"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"

        # Configuration des requêtes
        mock_session.query.return_value.filter.return_value.first.side_effect = [
            mock_existing_user,  # Première requête pour l'utilisateur
            None                 # Département introuvable
        ]

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'department': 'inexistant'
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        self.user_commands.console.print.assert_called()
        mock_session.close.assert_called_once()

    @patch('app.commands.user.User')
    @patch('app.commands.user.db_manager')
    def test_update_user_with_password(self, mock_db_manager, mock_user):
        """Test mise à jour avec nouveau mot de passe"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.name = "User Test"
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Mock du hashage de mot de passe
        mock_user.hash_password.return_value = "hashed_password"

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'name': 'User Modifié',
            'password': 'nouveau_password'
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        mock_user.hash_password.assert_called_once_with('nouveau_password')
        assert mock_existing_user.password_hash == "hashed_password"
        mock_session.commit.assert_called_once()

    @patch('app.commands.user.User')
    @patch('app.commands.user.db_manager')
    def test_update_user_with_empty_password(self, mock_db_manager, mock_user):
        """Test mise à jour avec mot de passe vide"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.name = "User Test"
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'name': 'User Modifié',
            'password': '   '  # Mot de passe vide avec espaces
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        mock_user.hash_password.assert_not_called()
        mock_session.commit.assert_called_once()

    @patch('app.commands.user.db_manager')
    def test_update_user_with_empty_values(self, mock_db_manager):
        """Test mise à jour avec valeurs vides (test du strip())"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.name = "User Test"
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'name': 'User Modifié',
            'mail': '   ',  # Valeur vide avec espaces - ne sera pas appliquée
            'username': 'nouveau.username'
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        mock_session.commit.assert_called_once()

    @patch('app.commands.user.db_manager')
    def test_update_user_exception(self, mock_db_manager):
        """Test exception lors de la mise à jour"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.department = Mock()
        mock_existing_user.department.name = "commercial"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Exception lors du commit
        mock_session.commit.side_effect = Exception("Erreur DB")

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1
        self.user_commands.user_view.get_user_update_form.return_value = {
            'name': 'User Modifié'
        }

        # Exécution
        self.user_commands.update_user()

        # Vérifications
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        self.user_commands.console.print.assert_called()

    @patch('app.commands.user.db_manager')
    def test_delete_user_success(self, mock_db_manager):
        """Test suppression d'utilisateur réussie"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.id = 1
        mock_existing_user.name = "User Test"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1

        # Exécution
        self.user_commands.delete_user()

        # Vérifications
        mock_session.delete.assert_called_once_with(mock_existing_user)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
        self.user_commands.console.print.assert_called()

    @patch('app.commands.user.db_manager')
    def test_delete_user_not_found(self, mock_db_manager):
        """Test suppression avec utilisateur introuvable"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Utilisateur introuvable
        mock_session.query.return_value.filter.return_value.first.return_value = None

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 999

        # Exécution
        self.user_commands.delete_user()

        # Vérifications
        self.user_commands.console.print.assert_called()
        mock_session.close.assert_called_once()

    @patch('app.commands.user.db_manager')
    def test_delete_user_exception(self, mock_db_manager):
        """Test exception lors de la suppression"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock de l'utilisateur existant
        mock_existing_user = Mock()
        mock_existing_user.name = "User Test"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_existing_user

        # Exception lors de la suppression
        mock_session.delete.side_effect = Exception("Erreur DB")

        # Mock des vues
        self.user_commands.list_users = Mock()
        self.user_commands.user_view.get_user_id.return_value = 1

        # Exécution
        self.user_commands.delete_user()

        # Vérifications
        mock_session.rollback.assert_called_once()
        mock_session.close.assert_called_once()
        self.user_commands.console.print.assert_called()

    @patch('app.commands.user.db_manager')
    def test_list_users_all(self, mock_db_manager):
        """Test listage de tous les utilisateurs"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des utilisateurs
        mock_user1 = Mock()
        mock_user1.department = Mock()
        mock_user1.department.name = "commercial"
        mock_user2 = Mock()
        mock_user2.department = Mock()
        mock_user2.department.name = "support"
        mock_users = [mock_user1, mock_user2]

        mock_session.query.return_value.all.return_value = mock_users

        # Exécution
        self.user_commands.list_users()

        # Vérifications
        self.user_commands.user_view.display_user_list.assert_called_once_with(mock_users)
        mock_session.close.assert_called_once()

    @patch('app.commands.user.Department')
    @patch('app.commands.user.db_manager')
    def test_list_users_filtered_by_department(self, mock_db_manager, mock_department):
        """Test listage filtré par département"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock des utilisateurs filtrés
        mock_user = Mock()
        mock_user.department = Mock()
        mock_user.department.name = "commercial"
        mock_users = [mock_user]

        mock_session.query.return_value.join.return_value.filter.return_value.all.return_value = mock_users

        # Exécution
        self.user_commands.list_users(filter_by_department="commercial")

        # Vérifications
        self.user_commands.user_view.display_user_list.assert_called_once_with(mock_users)
        mock_session.close.assert_called_once()

    @patch('app.commands.user.db_manager')
    def test_list_users_with_user_without_department(self, mock_db_manager):
        """Test listage avec utilisateur sans département"""
        # Mock de la session
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session

        # Mock d'utilisateur sans département
        mock_user = Mock()
        mock_user.department = None
        mock_users = [mock_user]

        mock_session.query.return_value.all.return_value = mock_users

        # Exécution
        self.user_commands.list_users()

        # Vérifications
        self.user_commands.user_view.display_user_list.assert_called_once_with(mock_users)
        mock_session.close.assert_called_once()

    @patch('app.commands.user.db_manager')
    def test_list_users_exception(self, mock_db_manager):
        """Test exception dans list_users"""
        # Mock de la session qui lève une exception
        mock_session = Mock()
        mock_db_manager.get_session.return_value = mock_session
        mock_session.query.side_effect = Exception("Erreur DB")

        # Exécution
        self.user_commands.list_users()

        # Vérifications
        self.user_commands.console.print.assert_called()
        mock_session.close.assert_called_once()

    def test_init_with_current_user(self):
        """Test du constructeur avec current_user"""
        user = Mock()
        user_commands = UserCommands(current_user=user)

        assert user_commands.current_user == user

    def test_init_without_current_user(self):
        """Test du constructeur sans current_user"""
        user_commands = UserCommands()

        assert user_commands.current_user is None
