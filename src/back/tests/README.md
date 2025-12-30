# Tests Documentation

## 🚀 Quick Start

```bash
# Installer les dépendances du projet
uv pip install -r build/python/requirements.txt

# Installer les dépendances de test
uv pip install -r src/back/tests/requirements-test.txt

# Lancer tous les tests
uv run pytest src/back/tests/ -v

# Avec couverture
uv run pytest src/back/tests/ --cov -v
```

## 📊 Status

| Module | Tests | Couverture |
|--------|-------|-----------|
| Playlists | 17 | 100% ✅ |
