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
        {"option": "3", "title": "Filtrer les événements"},
        {"option": "4", "title": "Consulter tous les clients"},
        {"option": "5", "title": "Consulter tous les contrats"},
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

    # Sous-menus pour SUPPORT
    "support_mes_evenements": [
        {"option": "1", "title": "Lister mes événements assignés"},
        {"option": "2", "title": "Rechercher un de mes événements"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "support_modifier_evenements": [
        {"option": "1", "title": "Modifier les détails d'un événement"},
        {"option": "2", "title": "Mettre à jour les notes d'un événement"},
        {"option": "3", "title": "Modifier la localisation"},
        {"option": "4", "title": "Modifier le nombre de participants"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "support_filtres_evenements": [
        {"option": "1", "title": "Mes événements assignés"},
        {"option": "2", "title": "Événements par date"},
        {"option": "3", "title": "Événements par nombre de participants"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "support_consulter_clients": [
        {"option": "1", "title": "Lister tous les clients"},
        {"option": "2", "title": "Rechercher un client"},
        {"option": "3", "title": "Voir les détails d'un client"},
        {"option": "0", "title": "Retour au menu principal"}
    ],
    "support_consulter_contrats": [
        {"option": "1", "title": "Lister tous les contrats"},
        {"option": "2", "title": "Rechercher un contrat"},
        {"option": "3", "title": "Voir les détails d'un contrat"},
        {"option": "0", "title": "Retour au menu principal"}
    ]
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
    "support": {
        "1": "support_mes_evenements",
        "2": "support_modifier_evenements",
        "3": "support_filtres_evenements",
        "4": "support_consulter_clients",
        "5": "support_consulter_contrats"
    }
}
