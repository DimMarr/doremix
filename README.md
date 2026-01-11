
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

CORS_ORIGINS=http://localhost:8080,https://localhost:8080
RATE_LIMIT=50/minute
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

Si rien ne s'affiche sur l'application web, vérifiez que les cors sont bien configurés dans le .env :
```
CORS_ORIGINS=http://localhost:8080,https://localhost:8080
```


# Processus de test

### Prérequis :
- uv
- pip

## Setup

```bash
# Installer les dépendances
uv pip install -r tests/requirements-test.txt

# Lancer tous les tests
uv run pytest tests/ -v

# Avec couverture
uv run pytest tests/ --cov -v
```

# Sécurité

## Frontend

### Injections xss

Vérifier s'il y a des injections xss possibles :

```bash
npx run xss-scan
```

Pour indiquer au système de templating qu'il faut échapper des caractères, on ajoute l'attribut `safe` :

```html
<span safe class="font-medium track-title">{track.title}</span>
```

Parfois, certaines données dynamiques sont considérées comme sûres car elles sont générées par le script lui-même et ne proviennent pas de l'utilisateur ; dans ce cas, il n'est pas nécessaire de les échapper.

```html
<div>{playlistCards as 'safe'}</div>
```
