from datetime import datetime
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr


class DateTracked:
    @declared_attr
    def created_at(cls):
        """
        Date de création de l'enregistrement
        """
        return Column(DateTime, default=datetime.now, nullable=False)

    @declared_attr
    def last_updated_at(cls):
        """
        Date de dernière modification de l'enregistrement
        """
        return Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)

    def update_last_updated(self):
        """
        Méthode pour mettre à jour manuellement la date de dernière modification
        """
        self.last_updated_at = datetime.now()