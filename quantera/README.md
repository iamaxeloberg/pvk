# Quantera.ai

AI-driven financial document indexing and query system for private equity and fund capital market firms.

## Overview

Quantera processes unstructured financial documents (PDF, Excel, CSV) and makes them queryable through a natural language interface. The system uses a two-stage LLM pipeline to balance cost efficiency with response quality, with optional vector-based semantic search for scalable retrieval.

## Architecture

```
Input Files (PDF/Excel/CSV)
    ↓
Converter → Markdown (Marker for PDF, openpyxl for Excel, csv stdlib for CSV)
    ↓
Low-cost LLM → Categorisation (company, categories)
    ↓
SQLite Index + Vector Embeddings (optional)
    ↓
User Query → Semantic Search / LLM Retrieval → Relevant Docs → Claude → Response
```

## Setup

```bash
# Install dependencies
make install

# Optional: install with vector search support
make install-vector

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Usage

### CLI

```bash
# Run the ingestion pipeline
make ingest

# Query indexed documents
make query Q="How is TechCorp performing?"

# List indexed documents
make list

# Generate synthetic test data
make seed
```

### Web API

```bash
# Start the FastAPI server
make serve
```

The API provides the following endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/ingest` | Run ingestion pipeline |
| `POST` | `/query` | Query with JSON body `{"question": "..."}` |
| `GET` | `/documents` | List all indexed documents |
| `DELETE` | `/documents/{path}` | Delete a document from the index |

Interactive API docs available at `http://localhost:8000/docs` when the server is running.

## Project Structure

```
├── config/          # Configuration (Pydantic Settings)
├── data/            # Input files, Markdown output, SQLite DB
├── prompts/         # LLM prompt templates
├── src/             # Core pipeline modules
│   ├── api.py       # CLI entry point
│   ├── web.py       # FastAPI web server
│   ├── ingestion.py # File detection and validation
│   ├── converter.py # PDF/Excel/CSV to Markdown
│   ├── categoriser.py # Low-cost LLM metadata extraction
│   ├── indexer.py   # SQLite storage and querying
│   ├── retriever.py # LLM-based index filtering
│   ├── generator.py # High-capacity LLM response generation
│   ├── chunker.py   # Document chunking with overlap
│   ├── vector_search.py # Semantic search with embeddings
│   └── utils.py     # Shared helpers + logging setup
├── tests/           # Test suite
├── scripts/         # CLI runners and utilities
├── logs/            # Application logs (auto-created)
├── Makefile         # Development task runner
└── .github/workflows/ # GitHub Actions CI
```

## Pipeline Stages

| Stage | Module | Description |
|-------|--------|-------------|
| DP1 | `ingestion.py` | File detection and validation |
| DP2 | `converter.py` | PDF/Excel/CSV → Markdown conversion |
| DP3-DP4 | `categoriser.py` | Low-cost LLM metadata extraction |
| DP5 | `indexer.py` | SQLite indexing |
| AL1-AL3 | `retriever.py` | LLM-based relevant document filtering |
| RG1-RG2 | `generator.py` | Claude response generation |

## Features

### Document Conversion
- **PDF** → Markdown via Marker
- **Excel** (.xlsx/.xls) → Markdown tables via openpyxl
- **CSV** → Markdown table via Python csv module

### Retrieval
- **LLM-based filtering** — default, works out of the box
- **Vector semantic search** — optional, requires `sentence-transformers` (`make install-vector`). Falls back to LLM retrieval when unavailable.

### Ingestion
- **Deduplication** — skips already-converted and already-indexed files
- **Status reporting** — summary table after each run showing successes, skips, and failures

### Document Chunking
- Paragraph-aware splitting with configurable overlap (`CHUNK_SIZE`, `CHUNK_OVERLAP` in `.env`)
- Prevents large documents from exceeding LLM context windows

### Logging
- Centralized logging to console and `logs/quantera.log`
- Configurable via `setup_logging()` in `src/utils.py`

## Development

```bash
# Run tests
make test

# Lint
make lint

# Format code
make format

# Clean generated files
make clean
```

## CI/CD

GitHub Actions runs on every push and pull request:
- **Lint** — ruff check
- **Test** — pytest with coverage on Python 3.10, 3.11, 3.12

## Configuration

All settings are configurable via `.env` file. See `.env.example` for reference.

| Variable | Default | Description |
|----------|---------|-------------|
| `LOW_COST_LLM_MODEL` | `deepseek/deepseek-chat` | Model for categorisation and retrieval |
| `HIGH_CAPACITY_LLM_MODEL` | `anthropic/claude-3-5-sonnet-20241022` | Model for response generation |
| `CHUNK_SIZE` | `4000` | Max characters per document chunk |
| `CHUNK_OVERLAP` | `200` | Characters of overlap between chunks |
| `DB_PATH` | `data/quantera.db` | SQLite database path |
| `INPUT_DIR` | `data/input` | Input directory for source files |
| `MARKDOWN_DIR` | `data/markdown` | Output directory for converted Markdown |
