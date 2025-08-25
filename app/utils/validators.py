import re


def validate_email(mail):
    """
    Contrôle si l'email est valide à l'aide d'un regex
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, mail):
        raise ValueError(f"Email invalide: {mail}")


def validate_tel(phone):
    """
    Contrôle si le téléphone est valide à l'aide d'un regex

    Suppression des espaces, tirets, points et parenthèses
    Contrôle que cela commence par un + et si c'est suivi de 10 à 15 chiffres
    """
    clean_tel = re.sub(r'[\s\-().]', '', phone)
    pattern = r'^\+?[0-9]{10,15}$'

    if not re.match(pattern, clean_tel):
        raise ValueError(f"Numéro de téléphone invalide: {phone}")