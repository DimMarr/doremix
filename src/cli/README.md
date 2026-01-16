Pré-requis : `uv`, `vlc`

## Initialisation de la CLI
#### Pour le dev :
``` bash
# À la racine du projet :
$ printf "\nAPI_BASE_URL=http://localhost:8000" >> .env
$ docker compose up
```
#### Pour la prod :
``` bash
# À la racine du projet :
$ printf "\nAPI_BASE_URL=http://fornax.dopolytech.fr:8000" >> .env
```

## Gestion du paquet doremix-cli

```bash
# Pour installer le paquet
$ cd src/cli
$ uv tool install [-e] . # -e rend le code source éditable
```
```bash
# Pour déinstaller le paquet
$ uv tool uninstall doremix-cli
```

## Commandes
```
doremix
    |- playlist
        |- list
        |- get <playlist-id>
        |- tracks <playlist-id>
        |- remove <playlist-id> <track-id>
        |- create --name <playlist-name> [--genre <genre-id>] [--visibility <visibility>]
        |- delete <playlist-id>
        |- update <playlist-id> [--name <playlist-name>] [--genre <genre-id>] [--visibility <visibility>]
        |- add-track <playlist-id> --url <youtube-link> --title <title>
        |- search-tracks <playlist-id> <query>
        |- search <query>
    |- track
        |- list
        |- get <track-id>
        |- play <track-id>
        |- stop
        |- search <query>
```
