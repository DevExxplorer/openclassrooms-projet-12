MESSAGES = {
    "welcome": "[cyan]=====Bienvenue dans l'outil EPIC Events=====[/cyan]",
    "invalid_option": "[red]L'option choisie n'existe pas[/red]",
    "invalid_user": "[red]Nom d'utilisateur ou mot de passe incorrect[/red]",
    "invalid_department": "[red]Département introuvable[/red]"
}

MENU = {
    "gestion": [
        {"option": "1", "title": "Gestion des collaborateurs"},
        {"option": "2", "title": "Gestion des contrats"},
        {"option": "3", "title": "Gestion des événements"},
        {"option": "5", "title": "Consulter tous les clients"},
        {"option": "0", "title": "Se déconnecter"}
    ],
    "commercial": [
        {"option": "1", "title": "Mes clients"},
        {"option": "2", "title": "Créer un client"},
        {"option": "3", "title": "Mes contrats"},
        {"option": "4", "title": "Filtrer les contrats"},
        {"option": "5", "title": "Créer un événement"},
        {"option": "0", "title": "Se déconnecter"}
    ],
    "support": [
        {"option": "1", "title": "Mes événements assignés"},
        {"option": "2", "title": "Mettre à jour mes événements"},
        {"option": "3", "title": "Consulter tous les clients"},
        {"option": "4", "title": "Consulter tous les contrats"},
        {"option": "0", "title": "Se déconnecter"}
    ]
}

SUBMENUS = {
    # Sous-menus pour GESTION
    "gestion_collaborateurs": [
        {"option": "1", "title": "Créer un collaborateur"},
        {"option": "2", "title": "Modifier un collaborateur"},
        {"option": "3", "title": "Supprimer un collaborateur"},
        {"option": "4", "title": "Lister tous les collaborateurs"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "gestion_contrats": [
        {"option": "1", "title": "Créer un contrat"},
        {"option": "2", "title": "Modifier un contrat"},
        {"option": "3", "title": "Lister tous les contrats"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "gestion_evenements": [
        {"option": "1", "title": "Modifier un événement"},
        {"option": "2", "title": "Assigner un support à un événement"},
        {"option": "3", "title": "Lister tous les événements"},
        {"option": "4", "title": "Événements sans support assigné"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "gestion_filtres_evenements": [
        {"option": "1", "title": "Événements sans support assigné"},
        {"option": "0", "title": "Retour au menu principal"}
    ],

    # Sous-menus pour COMMERCIAL
    "commercial_mes_clients": [
        {"option": "1", "title": "Lister mes clients"},
        {"option": "2", "title": "Modifier un de mes clients"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "commercial_mes_contrats": [
        {"option": "1", "title": "Lister mes contrats"},
        {"option": "2", "title": "Modifier un de mes contrats"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "commercial_filtres_contrats": [
        {"option": "1", "title": "Contrats non signés"},
        {"option": "2", "title": "Contrats non entièrement payés"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
}

MENU_MAPPING = {
    "gestion": {
        "1": "gestion_collaborateurs",
        "2": "gestion_contrats",
        "3": "gestion_evenements",
        "4": "gestion_filtres_evenements"
    },
    "commercial": {
        "1": "commercial_mes_clients",
        "3": "commercial_mes_contrats",
        "4": "commercial_filtres_contrats"
    },
    "support": {}
}

DIRECT_ACTIONS = {
    ("commercial", "2"): "create_client",
    ("commercial", "5"): "create_event",
    ("gestion", "5"): "list_all_clients",
    ("support", "1"): "list_assigned_events",
    ("support", "2"): "update_event",
    ("support", "3"): "list_all_clients",
    ("support", "4"): "list_all_contracts"
}
