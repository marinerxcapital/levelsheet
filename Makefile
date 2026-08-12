.PHONY: install dev-install lint format typecheck test test-cov run-gui run-cli bootstrap-cache docker-build docker-run clean

install:
	pip install -e .

dev-install:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/

format:
	black src/ tests/
	ruff check --fix src/ tests/

typecheck:
	mypy --strict src/

test:
	pytest tests/unit tests/integration -v

test-cov:
	pytest --cov=src/levelsheet --cov-report=term-missing --cov-fail-under=90

run-gui:
	streamlit run src/levelsheet/gui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

run-cli:
	python -m levelsheet generate $(SYMBOL) --date $(DATE) --format pdf,png

bootstrap-cache:
	python scripts/bootstrap_cache.py

docker-build:
	docker build -t levelsheet:latest .

docker-run:
	docker-compose up

clean:
	rm -rf output/pdf/* output/png/* logs/*.log __pycache__ .pytest_cache .mypy_cache .ruff_cache
