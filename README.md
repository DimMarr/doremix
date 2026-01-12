# DoRéMix

Application et CLI de gestion de playlists Youtube.

# Application web

### Prérequis :
- NPM
- Docker

## Setup en mode développement

```bash
# Déplacez vous dans le bon répértoire
cd src/frontend

# Il faut installer les dépendances
npm install

# Ensuite il faut exécuter l'application
npm run dev
```

## Setup en mode production

Mettre en place un fichier .env dans la racine du projet :

```
DB_USER=<DB_USERNAME>
DB_PASSWORD=<DB_PASSWORD>
DB_NAME=<DB_NAME>
DATABASE_URL=postgresql://<DB_USERNAME>:<DB_PASSWORD>@db:5432/<DB_NAME>
```

Démarrer l'infrastructure docker avec la commande suivante :

```bash
docker compose up
```

## Troubleshooting

En cas de problème en mode développement essayez de réinstaller les dépendences à zéro.

```bash
rm -rf node_modules package-lock.json
npm install
```

En cas de problème avec l'infrastructure docker essayez de désactiver docker buildkit :

```
export DOCKER_BUILDKIT=0
```

Sinon essayez de rebuild l'infrastructure docker depuis le début :

```
docker compose up --build
```

# Tests

### Prérequis :
- uv
- pip

## Setup

```bash
# Installer les dépendances du projet
uv pip install -r build/backend/requirements.txt

# Installer les dépendances de test
uv pip install -r src/back/tests/requirements-test.txt

# Lancer tous les tests
uv run pytest -v

# Avec couverture
uv run pytest --cov -v
```
