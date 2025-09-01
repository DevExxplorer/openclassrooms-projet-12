from app.database.db import db_manager
from app.models import Client


def check_and_create_database():
    """
    Vérifie si les tables existent, les créer si nécessaire
    """
    if not db_manager.tables_exist():
        db_manager.create_tables()
        print("✅ Base de données initialisée !")
    else:
        print('La Base de données a déjà été initialisé')

        client = Client()
        print(client.create(name="Dupont", mail="dupont@email.com", company_name="ACME Corp", role="commercial"))

        ## ERREUR À gérer
        # si email client existe déja
        # champs qui peuvent etre vide a verifier

        ## pour mes tests a supprimer apres

if __name__ == "__main__":
    check_and_create_database()
