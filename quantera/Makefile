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
	python3 -m pip install -e ".[dev]"

install-vector:
	python3 -m pip install -e ".[dev,vector]"

serve:
	python3 -m uvicorn src.web:app --reload --host 0.0.0.0 --port 8000

ingest:
	python3 src/api.py ingest

query:
ifndef Q
	$(error Q is required. Usage: make query Q='your question')
endif
	python3 src/api.py query "$(Q)"

list:
	python3 src/api.py list

seed:
	python3 scripts/seed_test_data.py

classify:
ifndef Q
	$(error Q is required. Usage: make classify Q='your question')
endif
	python3 src/api.py classify "$(Q)"

kpi:
ifndef COMPANY
	$(error COMPANY is required. Usage: make kpi COMPANY='TechCorp')
endif
	python3 src/api.py kpi "$(COMPANY)"

kpi-metric:
ifndef COMPANY
	$(error COMPANY is required. Usage: make kpi-metric COMPANY='TechCorp' METRIC='Revenue')
endif
ifndef METRIC
	$(error METRIC is required. Usage: make kpi-metric COMPANY='TechCorp' METRIC='Revenue')
endif
	python3 src/api.py kpi "$(COMPANY)" "$(METRIC)"

validate:
ifndef LABELS
	$(error LABELS is required. Usage: make validate LABELS=path/to/labels.json)
endif
	python3 scripts/validate_categorisation.py --labels "$(LABELS)"

test:
	python3 -m pytest tests/ -v

lint:
	python3 -m ruff check .

format:
	python3 -m ruff format .

clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache logs/
	rm -f data/quantera.db
	rm -f data/markdown/*.md
