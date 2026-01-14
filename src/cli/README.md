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
    |- add <playlist-id> <track-id> (WIP)
|- track
    |- get <track-id> (WIP)
    |- play [track-id] (WIP)
    |- stop (WIP)
    |- pause (WIP)
