# Tests Documentation

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
