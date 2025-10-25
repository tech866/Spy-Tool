# Makefile for Ad Intelligence Platform

.PHONY: help setup up down logs clean test seed

help:
	@echo "Ad Intelligence Platform - Make Commands"
	@echo ""
	@echo "  make setup    - Initial setup (copy env files, generate seed data)"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Show logs"
	@echo "  make clean    - Clean up containers and volumes"
	@echo "  make seed     - Load seed data into database"
	@echo "  make test     - Run tests"
	@echo ""

setup:
	@echo "Setting up environment..."
	cp -n backend/.env.example backend/.env || true
	cp -n frontend/.env.example frontend/.env || true
	@echo "Generating seed data..."
	python3 seed/generate_seed.py
	@echo "Setup complete! Run 'make up' to start services."

up:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Waiting for services to be healthy..."
	sleep 10
	@echo "Services started!"
	@echo ""
	@echo "Frontend: http://localhost:3000"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/api/docs"
	@echo "MinIO: http://localhost:9001 (minioadmin/minioadmin)"

down:
	@echo "Stopping services..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf backend/__pycache__ backend/app/__pycache__
	rm -rf frontend/.next frontend/node_modules

seed:
	@echo "Loading seed data..."
	sleep 5
	curl -X POST http://localhost:8000/api/v1/ingest/import \
		-H "Content-Type: application/json" \
		-d @seed/seed_data.json
	@echo "Seed data loaded!"

test:
	@echo "Running backend tests..."
	cd backend && pytest tests/ -v
	@echo "Running frontend tests..."
	cd frontend && npm test
