Pré-requis : uv

À la racine du projet :
>> printf "\nAPI_BASE_URL=http://localhost:8000" >> .env
>> docker compose up

>> cd src/cli
>> uv sync
>> source .venv/bin/activate
>> python3 main.py
