ALEMBIC_INI=src/infrastructure/database/alembic.ini

DATABASE_HOST ?= 0.0.0.0
DATABASE_PORT ?= 6767

RESET := $(filter reset,$(MAKECMDGOALS))


.PHONY: setup-env
setup-env:
	@sed -i '' "s|^APP_CRYPT_KEY=.*|APP_CRYPT_KEY=$(shell openssl rand -base64 32 | tr -d '\n')|" .env
	@sed -i '' "s|^BOT_SECRET_TOKEN=.*|BOT_SECRET_TOKEN=$(shell openssl rand -hex 64 | tr -d '\n')|" .env
	@sed -i '' "s|^DATABASE_PASSWORD=.*|DATABASE_PASSWORD=$(shell openssl rand -hex 24 | tr -d '\n')|" .env
	@sed -i '' "s|^REDIS_PASSWORD=.*|REDIS_PASSWORD=$(shell openssl rand -hex 24 | tr -d '\n')|" .env
	@echo "Secrets updated. Check your .env file"

.PHONY: migration
migration:
	DATABASE_HOST=$(DATABASE_HOST) DATABASE_PORT=$(DATABASE_PORT) alembic -c $(ALEMBIC_INI) revision --autogenerate

.PHONY: migrate
migrate:
	alembic -c $(ALEMBIC_INI) upgrade head

.PHONY: downgrade
downgrade:
	@if [ -z "$(rev)" ]; then \
		echo "No revision specified. Downgrading by 1 step."; \
		alembic -c $(ALEMBIC_INI) downgrade -1; \
	else \
		alembic -c $(ALEMBIC_INI) downgrade $(rev); \
	fi

.PHONY: run-local
run-local:
ifneq ($(RESET),)
	@docker compose -f docker-compose.local.yml down -v
endif
	@docker compose -f docker-compose.local.yml up --build
	@docker compose logs -f


.PHONY: run-prod
run-prod:
ifneq ($(RESET),)
	@docker compose -f docker-compose.prod.external.yml down -v
endif
	@docker compose -f docker-compose.prod.external.yml up --build
	@docker compose logs -f


.PHONY: reset
reset:
	@: