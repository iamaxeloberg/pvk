# Quantera.ai

AI-driven financial document indexing and query system for private equity and fund capital market firms.

## Overview

Quantera processes unstructured financial documents (PDF, Excel, CSV) and makes them queryable through a natural language interface. The system uses a two-stage LLM pipeline to balance cost efficiency with response quality.

## Architecture

```
Input Files (PDF/Excel/CSV)
    ↓
Marker → Markdown
    ↓
Low-cost LLM → Categorisation (company, categories)
    ↓
SQLite Index
    ↓
User Query → Filter Index → Relevant Docs → Claude → Response
```

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## Usage

```bash
# Run the ingestion pipeline
python scripts/run_pipeline.py ingest

# Query indexed documents
python scripts/run_pipeline.py query "How is TechCorp performing?"

# Or directly
python src/api.py "How is TechCorp performing?"
```

## Project Structure

```
├── config/          # Configuration
├── data/            # Input files, Markdown output, SQLite DB
├── prompts/         # LLM prompt templates
├── src/             # Core pipeline modules
├── tests/           # Test suite
└── scripts/         # CLI runners and utilities
```

## Pipeline Stages

| Stage | Module | Description |
|-------|--------|-------------|
| DP1 | `ingestion.py` | File detection and validation |
| DP2 | `converter.py` | Marker PDF/Excel → Markdown |
| DP3-DP4 | `categoriser.py` | Low-cost LLM metadata extraction |
| DP5 | `indexer.py` | SQLite indexing |
| AL1-AL3 | `retriever.py` | Relevant document filtering |
| RG1-RG2 | `generator.py` | Claude response generation |
