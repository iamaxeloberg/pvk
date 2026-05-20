PYTHON := .venv/bin/python3

.PHONY: help install ingest query list seed test lint format clean serve

help:
	@echo "Quantera - AI-driven financial document indexing"
	@echo ""
	@echo "Usage:"
	@echo "  make install          Install dependencies"
	@echo "  make install-vector   Install with vector search support"
	@echo "  make serve            Start FastAPI web server"
	@echo "  make ingest           Run ingestion pipeline"
	@echo "  make query Q=         Query indexed documents (auto-routed)"
	@echo "  make list             List indexed documents"
	@echo "  make classify Q=      Show which agent would handle the query"
	@echo "  make kpi COMPANY=     Show KPI trends for a company"
	@echo "  make kpi-metric COMPANY= METRIC=  Show specific KPI trend"
	@echo "  make seed             Generate synthetic test data"
	@echo "  make validate LABELS= Run categorisation validation"
	@echo "  make test             Run test suite"
	@echo "  make lint             Run ruff linter"
	@echo "  make format           Run ruff formatter"
	@echo "  make clean            Remove generated files"

install:
	$(PYTHON) -m pip install -e ".[dev]"

install-vector:
	$(PYTHON) -m pip install -e ".[dev,vector]"

serve:
	$(PYTHON) -m uvicorn src.web:app --host 0.0.0.0 --port 8000

ingest:
	$(PYTHON) src/api.py ingest

query:
ifndef Q
	$(error Q is required. Usage: make query Q='your question')
endif
	$(PYTHON) src/api.py query "$(Q)"

list:
	$(PYTHON) src/api.py list

seed:
	$(PYTHON) scripts/seed_test_data.py

classify:
ifndef Q
	$(error Q is required. Usage: make classify Q='your question')
endif
	$(PYTHON) src/api.py classify "$(Q)"

kpi:
ifndef COMPANY
	$(error COMPANY is required. Usage: make kpi COMPANY='TechCorp')
endif
	$(PYTHON) src/api.py kpi "$(COMPANY)"

kpi-metric:
ifndef COMPANY
	$(error COMPANY is required. Usage: make kpi-metric COMPANY='TechCorp' METRIC='Revenue')
endif
ifndef METRIC
	$(error METRIC is required. Usage: make kpi-metric COMPANY='TechCorp' METRIC='Revenue')
endif
	$(PYTHON) src/api.py kpi "$(COMPANY)" "$(METRIC)"

validate:
ifndef LABELS
	$(error LABELS is required. Usage: make validate LABELS=path/to/labels.json)
endif
	$(PYTHON) scripts/validate_categorisation.py --labels "$(LABELS)"

test:
	$(PYTHON) -m pytest tests/ -v

lint:
	$(PYTHON) -m ruff check .

format:
	$(PYTHON) -m ruff format .

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache logs/
	rm -f data/quantera.db
	rm -f data/markdown/*.md
