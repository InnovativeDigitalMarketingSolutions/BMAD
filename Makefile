# BMAD Production Makefile

.PHONY: help install test test-all clean lint format setup clickup-setup health-check metrics

help: ## Toon deze help
	@echo "BMAD Production Commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Installeer dependencies
	pip install -r requirements.txt

setup: ## Setup development environment
	pip install -r requirements.txt
	python -m pytest --version

clickup-setup: ## Setup ClickUp integratie
	python clickup_id_finder.py

test: ## Run alle tests
	pytest tests/ -v

test-unit: ## Run unit tests
	pytest tests/ -m "not integration and not slow" -v

test-integration: ## Run integration tests
	pytest tests/integration/ -v

test-backend: ## Run backend tests
	pytest tests/backend/ -v

test-agents: ## Run agent tests
	pytest tests/agents/ -v

test-all: ## Run alle tests met coverage
	pytest --cov=bmad --cov-report=html --cov-report=term

clean: ## Clean build artifacts
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .llm_cache/

lint: ## Run linting
	flake8 bmad/ tests/
	pylint bmad/ tests/

format: ## Format code
	black bmad/ tests/
	isort bmad/ tests/

# Production commands
health-check: ## Run health checks
	python -c "from bmad.agents.core.monitoring import health_checker; print(health_checker.get_health_status())"

metrics: ## Toon metrics
	python -c "from bmad.agents.core.monitoring import metrics_collector; print(metrics_collector.get_prometheus_format())"

cache-stats: ## Toon cache statistieken
	python -c "from bmad.agents.core.redis_cache import cache; print(cache.get_stats())"

# Quick commands
quick-test: ## Snelle test run
	pytest tests/ -x --tb=short

dev: install ## Install en run tests
	make test

# Docker commands (voor toekomstige implementatie)
docker-build: ## Build Docker image
	@echo "Docker build not yet implemented"
	# docker build -t bmad .

docker-run: ## Run BMAD in Docker
	@echo "Docker run not yet implemented"
	# docker run -p 8000:8000 bmad 