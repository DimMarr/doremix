Pré-requis : uv

À la racine du projet :
>> printf "\nAPI_BASE_URL=http://localhost:8000" >> .env
>> docker compose up

>> cd src/cli
>> uv run main.py <arguments>

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
|- track
    |- list
    |- get <track-id>
    |- play <track-id>
    |- stop
