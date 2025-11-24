import pytest # noqa
from unittest.mock import Mock, patch, mock_open
from app.services.auth_service import AuthService


class TestAuthService:
    """Tests pour AuthService"""

    def setup_method(self):
        """Setup pour chaque test"""
        # Patch le Path dès la création
        with patch('app.services.auth_service.Path') as mock_path:
            mock_token_file = Mock()
            mock_path.home.return_value.__truediv__.return_value = mock_token_file

            self.auth_service = AuthService()
            self.auth_service.token_file = mock_token_file
            # Mock de la console pour éviter les vraies sorties
            self.auth_service.console = Mock()

    @patch('app.services.auth_service.User')
    @patch('builtins.input')
    @patch('app.services.auth_service.getpass.getpass')
    def test_authenticate_user_success_new_login(self, mock_getpass, mock_input, mock_user):
        """Test authentification réussie avec nouvelle connexion"""
        # Mock du token inexistant
        self.auth_service._check_existing_token = Mock(return_value=None)

        # Mock des inputs utilisateur
        mock_input.return_value = "testuser"
        mock_getpass.return_value = "testpass"

        # Mock de l'utilisateur authentifié
        mock_user_instance = Mock()
        mock_user_instance.id = 1
        mock_user_instance.username = "testuser"
        mock_user.authenticate.return_value = mock_user_instance

        # Mock de la sauvegarde du token
        self.auth_service._save_token = Mock()

        # Exécution
        result = self.auth_service.authenticate_user()

        # Vérifications
        assert result == mock_user_instance
        mock_user.authenticate.assert_called_once_with("testuser", "testpass")
        self.auth_service._save_token.assert_called_once_with(mock_user_instance)

    @patch('app.services.auth_service.User')
    @patch('builtins.open', new_callable=mock_open)
    @patch('app.services.auth_service.json.load')
    @patch('app.services.auth_service.jwt.decode')
    def test_check_existing_token_success(self, mock_jwt_decode, mock_json_load, mock_file, mock_user):
        """Test vérification de token existant valide"""
        # Mock du fichier token existant
        self.auth_service.token_file.exists.return_value = True
        # Mock du contenu JSON
        mock_json_load.return_value = {'token': 'valid_token'}

        # Mock du décodage JWT
        mock_jwt_decode.return_value = {'user_id': 1, 'username': 'testuser'}

        # Mock de l'utilisateur récupéré
        mock_user_instance = Mock()
        mock_user.get_by_id.return_value = mock_user_instance

        # Exécution
        result = self.auth_service._check_existing_token()

        # Vérifications
        assert result == mock_user_instance
        mock_user.get_by_id.assert_called_once_with(1)
        self.auth_service.console.print.assert_called()

    def test_check_existing_token_file_not_exists(self):
        """Test vérification avec fichier token inexistant"""
        # Mock du fichier inexistant
        self.auth_service.token_file.exists.return_value = False

        # Exécution
        result = self.auth_service._check_existing_token()

        # Vérifications
        assert result is None

    @patch('builtins.open', new_callable=mock_open)
    @patch('app.services.auth_service.json.dump')
    @patch('app.services.auth_service.jwt.encode')
    def test_save_token_success(self, mock_jwt_encode, mock_json_dump, mock_file):
        """Test sauvegarde de token réussie"""
        # Mock de l'utilisateur
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"

        # Mock de l'encodage JWT
        mock_jwt_encode.return_value = "encoded_token"

        # Exécution
        self.auth_service._save_token(mock_user)

        # Vérifications
        mock_jwt_encode.assert_called_once()
        mock_json_dump.assert_called_once()
        self.auth_service.console.print.assert_called()

    def test_logout_success(self):
        """Test déconnexion réussie"""
        # Mock du fichier token existant
        self.auth_service.token_file.exists.return_value = True

        # Exécution
        result = self.auth_service.logout()

        # Vérifications
        assert result is True
        self.auth_service.token_file.unlink.assert_called_once()
        self.auth_service.console.print.assert_called()

    def test_logout_no_token_file(self):
        """Test déconnexion sans fichier token"""
        # Mock du fichier token inexistant
        self.auth_service.token_file.exists.return_value = False

        # Exécution
        result = self.auth_service.logout()

        # Vérifications
        assert result is False

    def test_authenticate_user_existing_token_return_path(self):
        """Test du return dans authenticate_user avec token existant"""
        # Mock de l'utilisateur depuis le token
        mock_user = Mock()
        mock_user.id = 1
        self.auth_service._check_existing_token = Mock(return_value=mock_user)

        # Mock pour s'assurer qu'on n'appelle pas les autres méthodes
        with patch('builtins.input') as mock_input, \
                patch('app.services.auth_service.getpass.getpass') as mock_getpass:

            # Exécution
            result = self.auth_service.authenticate_user()

            # Vérifications
            assert result == mock_user  # ← Teste le return existing_user
            # Vérifier qu'on n'a pas demandé d'input (connexion directe)
            mock_input.assert_not_called()
            mock_getpass.assert_not_called()

    @patch('builtins.open', new_callable=mock_open)
    @patch('app.services.auth_service.json.load')
    @patch('app.services.auth_service.jwt.decode')
    @patch('builtins.print')
    def test_check_existing_token_exception_with_existing_file(self, mock_print, mock_jwt_decode, mock_json_load, mock_file):
        """Test exception dans _check_existing_token avec fichier existant"""
        # Mock du fichier token existant
        self.auth_service.token_file.exists.return_value = True

        # Mock du contenu JSON
        mock_json_load.return_value = {'token': 'invalid_token'}

        # Mock du décodage JWT qui lève une exception
        mock_jwt_decode.side_effect = Exception("Token invalide")

        # Exécution
        result = self.auth_service._check_existing_token()

        # Vérifications
        assert result is None
        # Vérifier que l'erreur est imprimée
        mock_print.assert_called_with("Erreur token: Token invalide")  # ← Teste le print
        # Vérifier que le fichier est supprimé
        self.auth_service.token_file.unlink.assert_called_once()  # ← Teste le unlink dans l'exception
