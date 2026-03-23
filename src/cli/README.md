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
    |- register
    |- login
    |- whoami
    |- logout
    |- playlist
        |- list [--scope accessible|mine|open|public]
        |- get <playlist-id>
        |- tracks <playlist-id>
        |- remove <playlist-id> <track-id>
        |- create --name <playlist-name> [--genre <genre-id>] [--visibility <visibility>]
        |- delete <playlist-id> [--force]
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
    |- admin
        |- playlist
            |- list
            |- tracks <playlist-id>
            |- update <playlist-id> [--name <name>] [--genre <genre-id>] [--visibility <visibility>]
            |- delete <playlist-id> [--force]
            |- add-track <playlist-id> --url <youtube-url> --title <title>
            |- remove-track <playlist-id> <track-id>
        |- genre
            |- list
            |- add --label <label>
            |- update <genre-id> --label <label>
            |- delete <genre-id> [--force]
```

Notes:
- Visibility values are `PUBLIC`, `PRIVATE`, `OPEN`.
- `playlist list` defaults to `--scope accessible` (your playlists + other users' `OPEN` and `PUBLIC` playlists).
- Admin commands require an authenticated account with role `ADMIN`.
