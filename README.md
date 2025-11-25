# Architecture Back-end Sécurisée avec Python et SQL

## Description

Ce projet implémente une architecture back-end robuste et sécurisée utilisant Python et SQL. Il s'agit du 12ème projet du parcours OpenClassrooms, conçu pour démontrer les bonnes pratiques en matière de développement back-end, de sécurité et de gestion de bases de données.

## Fonctionnalités principales

- Architecture back-end sécurisée avec Python
- Intégration avec base de données SQL
- Gestion des dépendances avec Poetry
- Authentification et autorisation
- Validation des données
- Gestion des erreurs

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Python 3.8+** - [Télécharger Python](https://www.python.org/downloads/)
- **Poetry 1.5+** (version actuelle : 2.1.1) - [Guide d'installation Poetry](https://python-poetry.org/docs/#installation)
- **Git** - [Télécharger Git](https://git-scm.com/downloads)
- PostgreSQL

## Installation

### 1. Cloner le projet

```bash
git clone git@github.com:DevExxplorer/openclassrooms-projet-12.git
cd openclassrooms-projet-12
```

### 2. Installer les dépendances

```bash
# 1. Installer Poetry (si pas déjà fait)
curl -sSL https://install.python-poetry.org | python3 -

# 2. Installer toutes les dépendances
poetry install

# 3. Activer l'environnement virtuel
poetry shell

# 3. Ou derniere version poetry
poetry env activate

# 4. Lancer le serveur
poetry run python main.py
```

## Configuration

### Variables d'environnement

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Base de données
DB_NAME=[dbname]
DB_USER=[user]
DB_PASSWORD=[dbpassword]
DB_HOST=localhost
DB_PORT=5432
MODE=prod
SECRET_KEY='*******'
DSN="******"
```

### Base de données

```bash
poetry run python main.py --dev-init
```

### Tests

```bash
# Exécuter tous les tests
poetry run pytest

# Tests avec couverture de code
poetry run pytest --cov=.
```

### Linting et formatage

```bash
poetry run flake8
```

## Architecture

```
openclassrooms-projet-12/
├── app/
│   ├── controller/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── event.py
│   │   └── user.py
│   ├── database/
│   │   ├── __init__.py
│   │   └── db.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── date_tracked.py
│   │   ├── department.py
│   │   ├── event.py
│   │   └── user.py
│   ├── services/
│   │   ├── auth_service.py
│   │   ├── command_router.py
│   │   ├── initialization.py
│   │   └── menu_service.py
│   ├── tests/
│   │   ├── commands/
│   │   ├── database/
│   │   ├── models/
│   │   ├── services/
│   │   ├── views/
│   │   ├── __init__.py
│   │   └── conftest.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   └── validators.py
│   ├── views/
│   │   ├── client.py
│   │   ├── contract.py
│   │   ├── event.py
│   │   ├── menu.py
│   │   └── user.py
│   └── __init__.py
├── .coverage
└── pyproject.toml
└── .env
└── .flake8
└── main.py
```

### Interface CLI

L'application propose une interface en ligne de commande interactive pour :

```bash

# Gestion des clients
- Créer un nouveau client
- Modifier les informations client
- Lister tous les clients

# Gestion des contrats
- Créer un nouveau contrat
- Modifier un contrat existant
- Lister les contrats
- Filtrer par statut

# Gestion des événements
- Créer un nouvel événement
- Assigner un support à un événement
- Modifier les détails d'un événement
```


## Sécurité

Le projet implémente plusieurs mesures de sécurité :

- Authentification JWT
- Validation des données d'entrée
- Chiffrement des mots de passe avec bcrypt


## Tests et qualité

- Tests unitaires et d'intégration avec pytest
- Couverture de code > 80%
- Linting avec flake8

## Auteur

**DevExxplorer** - [Profil GitHub](https://github.com/DevExxplorer)

---

*Projet développé dans le cadre du parcours OpenClassrooms - Développeur Python*