.PHONY: help install dev test eval seed demo lint docker-up docker-down

help:
	@echo "GigBid (AI-4016 R&D Assignment) Command Interface"
	@echo "------------------------------------------------"
	@echo "make install      Install Python dependencies"
	@echo "make dev          Run API and Web dev servers"
	@echo "make test         Run pytest unit, integration, and contract tests"
	@echo "make eval         Run full evaluation suite (R&D Questions A, B, C, & Extension X2)"
	@echo "make seed         Generate personas, policy pack, and job streams"
	@echo "make demo         Launch interactive GigSim + GigBid end-to-end demo"
	@echo "make lint         Run ruff checks"
	@echo "make docker-up    Start full stack in Docker containers"
	@echo "make docker-down  Stop Docker containers"

install:
	pip install -e ".[dev]"

dev:
	uvicorn apps.api.main:app --reload --port 8000 &
	cd apps/web && npm run dev

test:
	pytest -v tests/ mcp_servers/

eval:
	python evals/runners/tool_granularity_eval.py
	python evals/runners/judge_calibration.py
	python evals/runners/rag_eval.py
	python evals/runners/ablation.py
	python evals/runners/multi_agent_eval.py
	python evals/runners/injection_eval.py
	python evals/runners/budget_and_outcomes_eval.py
	python evals/runners/extension_ab_test.py

seed:
	python scripts/seed_data.py

demo:
	python scripts/run_demo.py

lint:
	ruff check .
	ruff format --check .

docker-up:
	docker compose -f infra/docker-compose.yml up -d --build

docker-down:
	docker compose -f infra/docker-compose.yml down

