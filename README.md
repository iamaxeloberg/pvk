# Quantera.ai

AI-driven financial document indexing and query system for private equity and fund capital market firms.

## Overview

Quantera processes unstructured financial documents (PDF, Excel, CSV) and makes them queryable through a natural language interface. The system uses a **two-stage LLM pipeline** to balance cost efficiency with response quality:

1. **Low-cost LLM** — handles categorisation, retrieval filtering, and query classification
2. **High-capacity LLM** — generates final responses, executive briefings, financial insights, and KPI extraction

An **agent router** automatically classifies incoming queries and delegates to the most appropriate specialised sub-agent. Optional vector-based semantic search provides scalable retrieval for large document collections.

## Quick Start

```bash
# 1. Install dependencies
make install

# Optional: install with vector search support
make install-vector

# 2. Configure environment
cp .env.example .env
# Edit .env and add your LLM API keys and API base URLs

# 3. Generate test data and run ingestion
make seed

# 4. Query the system
make query Q="What is TechCorp's revenue?"

# 5. Start the web API (interactive docs at http://localhost:8000/docs)
make serve
```

## Architecture

```
                          ┌──────────────────────────┐
                          │   Input Files (PDF/XLSX/CSV)  │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │  DP1: Ingestion           │
                          │  File detection, validation, dedup           │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │  DP2: Converter           │
                          │  PDF (Marker) / Excel (openpyxl) / CSV → Markdown           │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │  DP3-DP4: Categoriser     │
                          │  Low-cost LLM extracts company + categories           │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │  DP5: Indexer             │
                          │  SQLite index + optional vector embeddings           │
                          └────────────┬─────────────┘
                                       │
                          ┌────────────▼─────────────┐
                          │  User Query               │
                          └────────────┬─────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
          ┌────────▼───────┐  ┌───────▼───────┐  ┌──────▼──────┐
          │ Vector Search   │  │ AL1-AL3:      │  │ Agent       │
          │ (cosine sim)    │  │ Retriever     │  │ Router      │
          └────────┬───────┘  │ LLM filtering │  │ (classify)  │
                   │          └───────┬───────┘  └──────┬──────┘
                   │                  │                  │
                   └──────────────────┼──────────────────┘
                                      │ Relevant Documents
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
          ┌────────▼───────┐  ┌──────▼──────┐  ┌───────▼──────┐
          │ KPI Agent       │  │ Insight     │  │ Briefing     │
          │ Extract + store  │  │ Agent       │  │ Agent        │
          │ time-series      │  │ Deep        │  │ Executive    │
          │ (→ kpi_store)    │  │ analysis    │  │ briefings    │
          └────────┬───────┘  └──────┬──────┘  └───────┬──────┘
                   │                 │                 │
                   └─────────────────┼─────────────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  RG1-RG2: Generator   │
                          │  High-capacity LLM generates response           │
                          └──────────┬───────────┘
                                     │
                          ┌──────────▼───────────┐
                          │  Assessment           │
                          │  Evaluate accuracy, completeness, consistency           │
                          └──────────────────────┘
```

## Project Structure

```
├── config/
│   └── settings.py          # Pydantic-based configuration (loads from .env)
├── data/
│   ├── input/               # Source files (PDF, XLSX, CSV) go here
│   ├── markdown/            # Converted Markdown output
│   └── quantera.db          # SQLite database (auto-created)
├── prompts/                 # LLM prompt templates (.txt files)
│   ├── agent_router.txt     # Query classification prompt
│   ├── categorisation.txt   # Metadata extraction prompt
│   ├── executive_briefing.txt   # Briefing generation prompt
│   ├── financial_insights.txt   # Insight analysis prompt
│   ├── kpi_extraction.txt   # KPI extraction prompt
│   ├── master_prompt.txt    # General response generation prompt
│   └── retrieval.txt        # Document filtering prompt
├── scripts/
│   ├── seed_test_data.py        # Synthetic test data generator
│   ├── seed_database.py         # Pre-indexed database seeder
│   ├── run_pipeline.py          # End-to-end pipeline runner
│   ├── validate_categorisation.py   # Accuracy measurement against labels
│   └── demo_prep.py             # Demo environment preparation
├── src/
│   ├── api.py               # CLI entry point (ingest, query, classify, kpi, list)
│   ├── web.py               # FastAPI web server with interactive docs
│   ├── ingestion.py         # File detection, format validation, deduplication
│   ├── converter.py         # PDF/Excel/CSV → Markdown conversion
│   ├── categoriser.py       # Low-cost LLM metadata extraction (company + categories)
│   ├── chunker.py           # Paragraph-aware document chunking with overlap
│   ├── indexer.py           # SQLite document storage, indexing, and querying
│   ├── retriever.py         # LLM-based relevant document filtering
│   ├── vector_search.py     # Semantic search with sentence-transformers embeddings
│   ├── generator.py         # High-capacity LLM response generation (RG1-RG2)
│   ├── kpi_store.py         # KPI time-series storage and trend queries
│   ├── assessment.py        # Response quality evaluation framework
│   ├── utils.py             # Shared utilities (LLM wrapper, logging, JSON parsing)
│   └── agents/
│       ├── router.py        # AI-powered query classifier and agent router
│       ├── kpi_agent.py     # KPI extraction and formatting agent
│       ├── insight_agent.py # Financial analysis and insights agent
│       └── briefing_agent.py    # Executive briefing agent
├── tests/                   # Test suite (114 tests across 13 modules)
│   ├── test_agents.py       # Agent routing, KPI, insight, briefing tests
│   ├── test_assessment.py   # Accuracy evaluation tests
│   ├── test_categoriser.py  # Metadata extraction tests
│   ├── test_chunker.py      # Chunking logic tests
│   ├── test_converter.py    # File conversion tests
│   ├── test_generator.py    # Response generation tests
│   ├── test_indexer.py      # SQLite index tests
│   ├── test_ingestion.py    # File validation tests
│   ├── test_kpi_store.py    # KPI storage and trend tests
│   ├── test_pipeline.py     # End-to-end pipeline error handling
│   ├── test_retriever.py    # Document retrieval tests
│   ├── test_validation.py   # Categorisation validation metric tests
│   └── test_vector_search.py    # Embedding and semantic search tests
├── logs/                    # Application logs (auto-created)
├── .env.example             # Configuration template
├── pyproject.toml           # Project metadata, dependencies, tool config
├── Makefile                 # Development task runner
└── .github/workflows/       # GitHub Actions CI (lint + test on Python 3.10-3.12)
```

## Pipeline Stages

| Stage | Module | LLM | Description |
|-------|--------|-----|-------------|
| DP1 | `ingestion.py` | — | Detect, validate, and deduplicate input files |
| DP2 | `converter.py` | — | Convert PDF/Excel/CSV to Markdown |
| DP3-DP4 | `categoriser.py` | Low-cost | Extract company name and category tags |
| DP5 | `indexer.py` | — | Store metadata and file paths in SQLite |
| — | `chunker.py` | — | Split large documents into overlapping chunks |
| — | `vector_search.py` | — | (Optional) Generate and search embeddings |
| AL1-AL3 | `retriever.py` | Low-cost | Filter index for relevant documents |
| — | `agents/router.py` | Low-cost | Classify query and route to best agent |
| — | `agents/kpi_agent.py` | High-capacity | Extract KPIs, store as time-series |
| — | `agents/insight_agent.py` | High-capacity | Generate deep financial analysis |
| — | `agents/briefing_agent.py` | High-capacity | Create executive briefings |
| RG1-RG2 | `generator.py` | High-capacity | Generate final answer from documents |
| — | `assessment.py` | High-capacity | Evaluate response quality and accuracy |

## Features

### Document Conversion
- **PDF** → Markdown via [Marker](https://github.com/VikParuchuri/marker) (OCR-free, structure-preserving)
- **Excel** (.xlsx/.xls) → Markdown tables per sheet via openpyxl
- **CSV** → Markdown table via Python csv module

### Ingestion & Deduplication
- Skips already-converted Markdown files and already-indexed documents
- Summary table after each run showing successes, skips, and failures per file

### LLM Pipeline
- **Two-stage architecture** — low-cost model for filtering/categorisation, high-capacity model for generation
- **Configurable models** — any LiteLLM-compatible provider (OpenAI, Anthropic, Gemini, local proxies, etc.)
- **Retry & timeout** — automatic retries on transient failures with configurable attempts and timeouts

### Agent Router
Queries are automatically classified by an AI router and delegated to the most appropriate sub-agent:

| Agent | Trigger keywords | Output |
|-------|-----------------|--------|
| `kpi` | Revenue, EBITDA, margin, growth rate, financial metrics | Structured KPI time-series data |
| `insight` | Performance, analysis, risk, trends, valuation | Detailed financial analysis |
| `briefing` | Summary, overview, executive, key points | Formatted executive briefing |
| `general` | Fallback for any other question | Standard document-backed answer |

### Document Chunking
- Paragraph-aware splitting with configurable size and overlap
- Prevents large documents from exceeding LLM context windows
- Chunk metadata includes source file, position, and token estimate

### Retrieval Strategies
- **LLM-based filtering** — default, uses low-cost LLM to select relevant documents from the index
- **Vector semantic search** — optional, uses `sentence-transformers` (all-MiniLM-L6-v2) with cosine similarity. Falls back to LLM retrieval when the embedding model is unavailable

### KPI Time-Series Tracking
- Automatic extraction and storage of financial metrics with period information
- Multi-period KPI trends stored in segment-aware time order (Q1→Q4, H1→H2, Y→Y)
- Query KPI trends by company and metric via CLI, API, or programmatic interface

### Response Quality Assessment
- **Automated evaluation** of factual accuracy, completeness, and consistency
- **Assessment suite** — define test cases with expected answers, run against the system, and review scores
- **Report generation** — average scores, pass rates, and per-case breakdowns
- **Configurable pass threshold** — default 0.7 composite score

### Categorisation Validation
- Compare AI-extracted categories and company names against a labelled ground-truth dataset
- Metrics include precision, recall, F1-score, and company name normalisation
- JSON label file format for easy creation and version control

### Logging
- Centralized logging to console and `logs/quantera.log`
- Configurable log level via `setup_logging()` in `src/utils.py`

## CLI Commands

```bash
# Display all available commands
make help

# Run the ingestion pipeline (convert + categorise + index)
make ingest

# Query indexed documents (auto-routed to best agent)
make query Q="How is TechCorp performing?"

# List all indexed documents
make list

# Show which agent would handle a query
make classify Q="What are the key risks?"

# Show KPI trends for a company
make kpi COMPANY="TechCorp AB"

# Show specific KPI metric trend
make kpi-metric COMPANY="TechCorp AB" METRIC="Revenue"

# Generate synthetic test data and ingest
make seed

# Prepare demo environment with pre-indexed data
make demo-prep

# Validate categorisation accuracy against labels
make validate LABELS=path/to/labels.json

# Start the FastAPI web server
make serve
```

## Web API

```bash
make serve
```

Interactive OpenAPI docs available at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Run full ingestion pipeline |
| `POST` | `/query` | Query with JSON body `{"question": "..."}` — auto-routed to best agent |
| `POST` | `/classify` | Classify a query — returns agent name classification |
| `GET` | `/documents` | List all indexed documents with metadata |
| `DELETE` | `/documents/{path}` | Delete a document from the index by path |
| `GET` | `/kpi/companies` | List companies with stored KPI data |
| `GET` | `/kpi/{company}` | Get all KPIs for a company |
| `GET` | `/kpi/{company}/{metric}` | Get KPI time-series trend for a metric |

## Configuration

All settings are configured via `.env` file. Copy `.env.example` to `.env` and edit as needed.

### LLM Configuration

The system supports any LiteLLM-compatible provider. When using a local proxy like FreeLLMAPI, use the `openai/<model>` prefix format and set the API base to the proxy URL.

| Variable | Default | Description |
|----------|---------|-------------|
| `LOW_COST_LLM_MODEL` | `deepseek/deepseek-chat` | Model for categorisation, retrieval, and routing |
| `LOW_COST_LLM_API_KEY` | — | API key for the low-cost LLM |
| `LOW_COST_LLM_API_BASE` | — | Optional API base URL (e.g. `http://localhost:3001/v1`) |
| `HIGH_CAPACITY_LLM_MODEL` | `anthropic/claude-3-5-sonnet-20241022` | Model for response generation and insights |
| `HIGH_CAPACITY_LLM_API_KEY` | — | API key for the high-capacity LLM |
| `HIGH_CAPACITY_LLM_API_BASE` | — | Optional API base URL |
| `TEMPERATURE` | `0.0` | LLM sampling temperature (0 = deterministic) |
| `MAX_TOKENS` | `4096` | Max output tokens for LLM responses |

### Storage Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_PATH` | `data/quantera.db` | SQLite database path (WAL mode, busy timeout 5s) |
| `INPUT_DIR` | `data/input` | Directory for source files (PDF, XLSX, CSV) |
| `MARKDOWN_DIR` | `data/markdown` | Directory for converted Markdown output |

### Chunking & Size Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE` | `4000` | Max characters per document chunk |
| `CHUNK_OVERLAP` | `200` | Characters of overlap between consecutive chunks |
| `MAX_DOC_SIZE_CHARS` | `100000` | Max document size before truncation for LLM prompts |

## Development

```bash
# Install dev dependencies (pytest, ruff, pytest-cov)
make install

# Run all tests (114 tests, ~1.4 seconds)
make test

# Run linter (ruff check — E, F, I, N, W, UP rules)
make lint

# Auto-format code (ruff format, max line length 160)
make format

# Clean generated files (cache, database, markdown, logs)
make clean

# Create a distributable zip file for handover
make dist
```

## Testing

The project includes **114 tests across 13 test modules** covering all pipeline stages, sub-agents, edge cases, and error handling.

### Test Suite Overview

| Test File | Tests | What it covers |
|-----------|-------|---------------|
| `test_agents.py` | 18 | Agent router classification, KPI extraction/formatting, insight generation, briefing generation, agent integration |
| `test_assessment.py` | 10 | Assessment result scoring, pass/fail thresholds, report aggregation, LLM response evaluation, report file output |
| `test_categoriser.py` | 5 | Metadata extraction with mocked LLM, code fence handling, JSON parsing, malformed JSON error, long doc truncation |
| `test_chunker.py` | 7 | Small text passthrough, large text splitting, chunk metadata, sequential indices, empty text, token estimation, overlap preservation |
| `test_converter.py` | 2 | Empty batch handling, invalid file type rejection |
| `test_generator.py` | 6 | Prompt reading, no-doc response, missing doc handling, mocked generation, model selection, multi-doc combination |
| `test_indexer.py` | 8 | DB init, insert/retrieve, duplicate handling, company/category filtering, count, delete, existence check |
| `test_ingestion.py` | 6 | Supported extensions, file validation, nonexistent files, file discovery, empty/nonexistent directories |
| `test_kpi_store.py` | 10 | KPI table init, store/retrieve, trend ordering (quarter/year), company listing, metric listing, delete, non-numeric values |
| `test_pipeline.py` | 5 | Empty input dir, invalid file type, idempotent DB init, querying empty DB, missing file conversion |
| `test_retriever.py` | 7 | Index context building, empty context, prompt reading, mocked retrieval, invalid path filtering, empty response, multi-path |
| `test_validation.py` | 9 | Category perfect/partial/no match, case insensitivity, empty sets, company name normalisation, different companies |
| `test_vector_search.py` | 11 | Vector table init, embedding store/retrieve, missing embeddings, cosine similarity (identical/orthogonal/opposite/zero), search results, threshold/top-k respect, model fallback |

### Running Tests

```bash
# Run the full test suite
make test                              # 114 tests, ~1 second

# Run a specific test file
make test-file F=test_kpi_store.py    # or: python -m pytest tests/test_kpi_store.py -v

# Run a specific test class
python -m pytest tests/test_agents.py::TestAgentRouter -v

# Run a single test
python -m pytest tests/test_indexer.py::TestIndexer::test_init_db -v

# Run with coverage report
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

### How Tests Work

**Database tests** create temporary SQLite databases via `tempfile` — no persistent state is modified. Each test gets its own isolated database that is discarded afterward.

**LLM tests** use Python's `unittest.mock` to intercept LiteLLM API calls. Mocked responses return pre-written JSON that exercises specific scenarios (valid metadata, malformed JSON, empty responses, etc.). This means tests run offline — no API keys or network access required.

**Conversion tests** run against a `data/input/` directory that can be populated with test fixtures. The converter handles all three supported formats (PDF, XLSX, CSV).

**3 tests are skipped** when run without a live LLM backend, as they exercise the full request/response cycle. These tests have `@pytest.mark.skipif` decorators and do not affect the pass count.

### Generating Test Data

```bash
# Generate synthetic financial documents (4 Swedish companies)
make seed                              # Creates CSV files in data/input/

# Alternative: generate Acme Corp test data (CSV, XLSX, PDF)
python scripts/make_test_files.py
```

## CI/CD

GitHub Actions runs on every push and pull request to `main`:

- **Lint** — `ruff check` across the full codebase
- **Test** — `pytest` with coverage on Python 3.10, 3.11, and 3.12
- **Database** — tests use temporary SQLite databases, no external services needed
- **LLM** — tests use mocked LiteLLM responses, no API keys required in CI

## Handover / Distribution

To create a clean zip file for distribution:

```bash
make dist
```

This produces `quantera-{version}.zip` at the repository root, containing:
- All source code, prompts, scripts, and tests
- Configuration templates (`.env.example`, `pyproject.toml`)
- README and demo documentation
- Empty data directories ready for input files

The zip **excludes** virtual environments, databases, logs, cache files, IDE config, and any personal/team-internal documents.

## Requirements

- **Python** 3.10+
- **System** — `marker-pdf` may require PyTorch and system libraries for PDF processing
- **Optional** — `sentence-transformers` for vector search support
