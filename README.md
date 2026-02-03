# DoRéMix 🎵

**DoRéMix** is a collaborative music ecosystem developed for the **Python Web Agile (PWA)** project (DO3, 2025-2026). The platform allows users to curate and share community-driven playlists powered by YouTube, offering both a **Web Experience** and a **CLI tool**.

---

## 🌟 Features

* **Social Playlists:** Create, share, and discover playlists curated by the community.
* **YouTube Integration:** Seamlessly add tracks via YouTube URLs and listen via the integrated embedded player.
* **Dual-Interface:** Full control through a responsive Web App or a developer-friendly Command Line Interface.
* **Real-time Discovery:** Add new sounds and share them instantly with the community.

---

## 🛠 Tech Stack

| Layer | Technology |
| :--- | :--- |
| **Backend** | Python / FastAPI |
| **Frontend** | Modern JS (PWA Architecture) |
| **CLI** | Python / Typer |
| **Database** | PostgreSQL |
| **DevOps** | Docker & Docker Compose |
| **Package Management** | `uv` (Python), `npm` (Node.js) |

---

## 🚀 Getting Started

### Prerequisites
* **Docker & Docker Compose**
* **Node.js** (for frontend development)
* **Python 3.10+** (with `uv` installed for local testing/CLI)

### Local Development Setup
To launch the development environment with hot-reloading:

```bash
# 1. Initialize environment variables
cp .env.exemple .env

# 2. Build and launch infrastructure
docker compose up -d --build
```

Access Points:
- **Frontend**: http://localhost:8080
- **Backend API** (Swagger): http://localhost:8000/docs

---

## ⚙️ Configuration (Production Mode)

For production deployments, ensure your .env file at the root is properly configured:

```bash
# Database Configuration
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=doremix_db
DATABASE_URL=postgresql://${DB_USER}:${DB_PASSWORD}@db:5432/${DB_NAME}

# Security & Performance
RATE_LIMIT=50/minute
```

Then, run the infrastructure in production mode:

```bash
docker compose up -f docker-compose_prod.yml -d --build
```

---

## 🧪 Testing & Quality Assurance
We use uv for lightning-fast dependency management and pytest for our test suite.
```bash
# Synchronize environment
uv sync

# Run all tests
uv run pytest -v

# Run tests with coverage report
uv run pytest --cov -v
```
