from datetime import datetime
from unittest.mock import patch
from app.models.date_tracked import DateTracked


def test_update_last_updated():
    # Créer une classe qui hérite de DateTracked pour pouvoir l'instancier
    class TestModel(DateTracked):
        def __init__(self):
            # Simuler les attributs SQLAlchemy
            self.created_at = datetime(2020, 1, 1)
            self.last_updated_at = datetime(2020, 1, 1)

    # Créer une instance
    obj = TestModel()
    old_date = obj.last_updated_at

    # Mocker datetime.now() pour avoir une date prévisible
    fixed_time = datetime(2025, 1, 15, 10, 30, 0)
    with patch('app.models.date_tracked.datetime') as mock_datetime:
        mock_datetime.now.return_value = fixed_time

        # Appeler la méthode à tester
        obj.update_last_updated()

        # Vérifier que la date a été mise à jour
        assert obj.last_updated_at == fixed_time
        assert obj.last_updated_at != old_date
