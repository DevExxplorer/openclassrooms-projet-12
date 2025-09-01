from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import logging

# Cache les warnings dans la console
logging.getLogger('sqlalchemy').setLevel(logging.WARNING)

# Charger les variables du fichier .env
load_dotenv()

# Base pour tous nos modèles
Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        """
        Définir l'URL de connexion PostgreSQL
        Création du moteur de la base de donnée
        Création de la session
        """
        self.database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT', 5432)}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(self.database_url, echo=os.getenv('MODE') == 'dev')
        self.SessionLocal = sessionmaker(bind=self.engine)

    def tables_exist(self):
        """
        Vérifier si les tables existent dans la base de données
        """
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()

        # Récupérer les noms des tables définies dans vos modèles
        expected_tables = Base.metadata.tables.keys()

        # Vérifier si toutes les tables attendues existent
        return all(table in existing_tables for table in expected_tables)

    def create_tables(self):
        """
        Créer toutes les tables définies dans le dossier models
        """
        Base.metadata.create_all(bind=self.engine)
        print("Tables créées avec succès !")

    def get_session(self):
        """
        Obtenir une session de base de données
        """
        return self.SessionLocal()

    def drop_tables(self):
        """
        Supprimer toutes les tables (pour les tests)
        """
        Base.metadata.drop_all(bind=self.engine)
        print("Tables supprimées !")

db_manager = DatabaseManager()