# Makefile
.PHONY: help \
	docker docker-down up down logs-be logs-fe reset-db \
	local local-setup local-env local-be local-fe local-migrate local-stop \
	migrate-create migrate-up migrate-down migrate-history format lint test-be sync-rules \
	cloud-build cloud-push cloud-build-push cloud-deploy \
	deploy deploy-setup deploy-build deploy-status deploy-backend deploy-frontend

# Configuration (override with environment variables)
GCP_PROJECT ?= fde-rnd
GCP_REGION ?= us-central1
ARTIFACT_REPO ?= template-deployment
KEYCLOAK_IMAGE ?= us-central1-docker.pkg.dev/$(GCP_PROJECT)/$(ARTIFACT_REPO)/keycloak
KEYCLOAK_VERSION ?= v2

# Local (native, non-Docker) development configuration
VENV ?= .venv
LOCAL_BE_PORT ?= 8001
LOCAL_FE_PORT ?= 3000
LOCAL_DB_HOST ?= localhost

help:
	@echo "╔════════════════════════════════════════════════════════════════════╗"
	@echo "║              AI COMMAND CENTER - MAKEFILE COMMANDS                 ║"
	@echo "╚════════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "This project runs in 3 modes:  docker  |  local  |  cloud"
	@echo ""
	@echo "── DOCKER MODE (docker-compose) ─────────────────────────────────────"
	@echo "  docker | up        : Start all services (postgres, backend, frontend)."
	@echo "  docker-down | down : Stop all docker-compose services."
	@echo "  logs-be            : Tail backend container logs."
	@echo "  logs-fe            : Tail frontend container logs."
	@echo "  reset-db           : Clean and re-seed the DB (in the running container)."
	@echo ""
	@echo "── LOCAL MODE (native: Next.js + Python API, no Docker) ─────────────"
	@echo "  local-setup        : One-time setup: venv + pip install, npm install, .env.local."
	@echo "  local              : Run backend (uvicorn) AND frontend (next dev) together."
	@echo "  local-be           : Run only the FastAPI backend on port $(LOCAL_BE_PORT)."
	@echo "  local-fe           : Run only the Next.js frontend on port $(LOCAL_FE_PORT)."
	@echo "  local-migrate      : Apply Alembic migrations to your local database."
	@echo "  local-stop         : Stop locally-running backend/frontend processes."
	@echo "                       (Requires a local PostgreSQL reachable at $(LOCAL_DB_HOST).)"
	@echo ""
	@echo "── CLOUD MODE (Google Cloud Run) ────────────────────────────────────"
	@echo "  deploy             : Full production deployment (setup + build + deploy)."
	@echo "  deploy-setup       : Initial GCP setup (APIs, Cloud SQL, secrets)."
	@echo "  deploy-build       : Build and push Docker images."
	@echo "  deploy-backend     : Rebuild and redeploy backend only."
	@echo "  deploy-frontend    : Rebuild and redeploy frontend only."
	@echo "  deploy-status      : Show deployment status."
	@echo "  cloud-deploy       : Print the Keycloak Cloud Run deploy command."
	@echo "  cloud-build        : Build Keycloak image for Cloud Run."
	@echo "  cloud-push         : Push Keycloak image to Artifact Registry."
	@echo ""
	@echo "── SHARED (any mode) ────────────────────────────────────────────────"
	@echo "  migrate-create MSG='description' : Create a new Alembic migration (docker)."
	@echo "  migrate-up / migrate-down / migrate-history : Manage migrations (docker)."
	@echo "  format             : Format backend + frontend code."
	@echo "  lint               : Lint backend + frontend code."
	@echo "  test-be            : Run backend tests with pytest (docker)."
	@echo "  sync-rules         : Regenerate .cursor/rules/ mirror from .agents/rules/."

# ============================================================
# DOCKER MODE (docker-compose)
# ============================================================

# Alias so all three modes have a memorable entry point: docker / local / deploy
docker: up

docker-down: down

up:
	@echo "🚀 Starting all Supervity services..."
	docker-compose up --build -d

down:
	@echo "🛑 Stopping all Supervity services..."
	docker-compose down

logs-be:
	@echo "👀 Tailing backend logs..."
	docker-compose logs -f backend

logs-fe:
	@echo "👀 Tailing frontend logs..."
	docker-compose logs -f frontend

reset-db:
	@echo "🧹 Resetting the database..."
	docker-compose exec backend python scripts/reset_db.py
	@echo "🌱 Seeding database with initial data..."
	docker-compose exec backend python scripts/seed_db.py
	@echo "✅ Database reset complete!"

migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a message. Usage: make migrate-create MSG='your description'"; \
		exit 1; \
	fi
	@echo "🔄 Creating new migration: $(MSG)"
	docker-compose exec backend alembic revision --autogenerate -m "$(MSG)"
	@echo "✅ Migration created successfully!"

migrate-up:
	@echo "⬆️  Applying pending migrations..."
	docker-compose exec backend alembic upgrade head
	@echo "✅ All migrations applied!"

migrate-down:
	@echo "⬇️  Downgrading database by one migration..."
	docker-compose exec backend alembic downgrade -1
	@echo "✅ Database downgraded!"

migrate-history:
	@echo "📋 Migration history:"
	docker-compose exec backend alembic history --verbose 

format:
	@echo "🎨 Formatting backend Python code..."
	black .
	isort .
	@echo "🎨 Formatting frontend TypeScript/React code..."
	@npm --prefix frontend run format
	@echo "✅ Formatting complete!"

lint:
	@echo "🔍 Linting backend Python code..."
	flake8 .
	@echo "🔍 Linting frontend TypeScript/React code..."
	@npm --prefix frontend run lint
	@echo "✅ Linting complete!"

test-be:
	@echo "🧪 Running backend tests..."
	docker-compose exec backend pytest
	@echo "✅ Backend tests complete!"

sync-rules:
	@echo "🔁 Syncing .cursor/rules/ from canonical .agents/rules/..."
	@bash scripts/sync-rules.sh
	@echo "✅ Rule mirror up to date. Commit any changes."

# ============================================================
# LOCAL MODE (native: Next.js + Python API, no Docker)
# ============================================================
# Runs the FastAPI backend via uvicorn and the Next.js frontend via `next dev`
# directly on the host. Reads config from .env but overrides the DB host to
# $(LOCAL_DB_HOST) since the `postgres` docker hostname is not resolvable here.
# Requires a PostgreSQL instance reachable at $(LOCAL_DB_HOST):5432.

local-setup:
	@echo "🧰 Setting up local (non-Docker) dev environment..."
	@echo "🐍 Creating Python venv ($(VENV)) and installing backend deps..."
	python3 -m venv $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade pip && pip install -r packages/requirements.txt
	@echo "📦 Installing frontend deps..."
	cd frontend && npm install
	@$(MAKE) local-env
	@echo "✅ Local setup complete! Run 'make local' to start both servers."

local-env:
	@if [ ! -f .env ]; then \
		echo "📄 No .env found — copying from .env.example..."; \
		cp .env.example .env; \
		echo "✅ Created .env (review it and set secrets before running)."; \
	else \
		echo "ℹ️  .env already exists — leaving it untouched."; \
	fi
	@if [ ! -f frontend/.env.local ]; then \
		echo "📄 No frontend/.env.local found — copying from frontend/.env.local.example..."; \
		cp frontend/.env.local.example frontend/.env.local; \
		echo "✅ Created frontend/.env.local (set NEXTAUTH_SECRET before running)."; \
	else \
		echo "ℹ️  frontend/.env.local already exists — leaving it untouched."; \
	fi

local-be: local-env
	@echo "🐍 Starting FastAPI backend on http://localhost:$(LOCAL_BE_PORT) ..."
	@set -a; . ./.env; set +a; \
	export POSTGRES_HOST=$(LOCAL_DB_HOST); \
	export DATABASE_URL="postgresql://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$(LOCAL_DB_HOST):$${POSTGRES_PORT}/$${POSTGRES_DB}"; \
	export LOCAL_STORAGE_PATH="$$PWD/document_storage"; \
	mkdir -p "$$LOCAL_STORAGE_PATH"; \
	. $(VENV)/bin/activate; \
	uvicorn app.main:app --reload --host 0.0.0.0 --port $(LOCAL_BE_PORT)

local-fe: local-env
	@echo "⚛️  Starting Next.js frontend on http://localhost:$(LOCAL_FE_PORT) ..."
	cd frontend && npm run dev -- --port $(LOCAL_FE_PORT)

local: local-env
	@echo "🚀 Starting backend + frontend locally (Ctrl+C stops both)..."
	@trap 'kill 0' INT TERM EXIT; \
	$(MAKE) local-be & \
	$(MAKE) local-fe & \
	wait

local-migrate: local-env
	@echo "⬆️  Applying migrations to local database ($(LOCAL_DB_HOST))..."
	@set -a; . ./.env; set +a; \
	export DATABASE_URL="postgresql://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$(LOCAL_DB_HOST):$${POSTGRES_PORT}/$${POSTGRES_DB}"; \
	. $(VENV)/bin/activate; \
	alembic upgrade head
	@echo "✅ Local migrations applied!"

local-stop:
	@echo "🛑 Stopping locally-running backend/frontend..."
	-@pkill -f "uvicorn app.main:app" 2>/dev/null || true
	-@pkill -f "next dev" 2>/dev/null || true
	@echo "✅ Stopped (if they were running)."

# ============================================================
# Cloud Deployment Commands (Keycloak on Google Cloud Run)
# ============================================================

cloud-build:
	@echo "🔨 Building Keycloak image for Cloud Run (AMD64)..."
	docker buildx build --platform=linux/amd64 -f keycloak/Dockerfile.cloud -t $(KEYCLOAK_IMAGE):$(KEYCLOAK_VERSION) ./keycloak
	@echo "✅ Image built: $(KEYCLOAK_IMAGE):$(KEYCLOAK_VERSION)"

cloud-push:
	@echo "🚀 Pushing Keycloak image to Artifact Registry..."
	docker push $(KEYCLOAK_IMAGE):$(KEYCLOAK_VERSION)
	@echo "✅ Image pushed successfully!"

cloud-build-push:
	@echo "🔨 Building and pushing Keycloak image for Cloud Run..."
	docker buildx build --platform=linux/amd64 -f keycloak/Dockerfile.cloud -t $(KEYCLOAK_IMAGE):$(KEYCLOAK_VERSION) ./keycloak --push
	@echo "✅ Image built and pushed: $(KEYCLOAK_IMAGE):$(KEYCLOAK_VERSION)"

cloud-deploy:
	@echo "☁️  Deploying Keycloak to Cloud Run..."
	@echo "⚠️  Make sure you have:"
	@echo "    1. Created a Cloud SQL PostgreSQL instance"
	@echo "    2. Created a 'keycloak' database in the instance"
	@echo "    3. Set up the Cloud SQL connection"
	@echo ""
	@echo "Run this command manually with your settings:"
	@echo ""
	@echo "gcloud run deploy supervity-auth \\"
	@echo "  --image=$(KEYCLOAK_IMAGE):$(KEYCLOAK_VERSION) \\"
	@echo "  --platform=managed \\"
	@echo "  --region=$(GCP_REGION) \\"
	@echo "  --allow-unauthenticated \\"
	@echo "  --port=8080 \\"
	@echo "  --memory=1Gi \\"
	@echo "  --cpu=1 \\"
	@echo "  --min-instances=0 \\"
	@echo "  --max-instances=2 \\"
	@echo "  --set-env-vars='KC_DB=postgres,KC_DB_USERNAME=postgres,KC_PROXY=edge,KEYCLOAK_ADMIN=admin,KEYCLOAK_ADMIN_PASSWORD=admin' \\"
	@echo "  --add-cloudsql-instances=YOUR_CONNECTION_NAME"

# ============================================================
# Production Deployment Commands (Full Stack)
# ============================================================

deploy:
	@echo "🚀 Running full production deployment..."
	./deployment/deploy.sh all

deploy-setup:
	@echo "⚙️  Setting up GCP resources..."
	./deployment/deploy.sh setup

deploy-build:
	@echo "🔨 Building Docker images..."
	./deployment/deploy.sh build

deploy-backend:
	@echo "🔄 Redeploying backend..."
	./deployment/deploy.sh redeploy-backend

deploy-frontend:
	@echo "🔄 Redeploying frontend..."
	./deployment/deploy.sh redeploy-frontend

deploy-status:
	@echo "📊 Checking deployment status..."
	./deployment/deploy.sh status