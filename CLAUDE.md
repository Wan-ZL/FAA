# Finance Agent

## Project Overview
AI-powered financial analysis engine with multi-agent collaboration. CLI-first, analysis-only (no trade execution).

## Tech Stack
- Python 3.12+, Anthropic SDK, Pydantic v2
- Storage: Neo4j (KG), ChromaDB (vectors), DuckDB (time series), SQLite WAL (shared board)
- Data: yfinance, FRED, SEC EDGAR, FinnHub, TA-Lib/pandas-ta, QuantLib

## Project Structure
- `src/finance_agent/` - Main package
  - `agent/` - Agent loop, team management, debate mechanism
  - `data/` - Provider registry, fetchers, data models
  - `tools/` - Tool definitions grouped by domain
  - `memory/` - Storage interfaces (board, KG, vectors, time series)
  - `mcp/` - MCP server
  - `cli.py` - Rich CLI interface
  - `config.py` - Configuration (pydantic-settings)

## Conventions
- All data flows through Provider Registry via TET pipeline (Transform -> Enrich -> Tag)
- Agents communicate via SharedStateBoard (SQLite WAL), not direct messages
- Tools use @function_tool decorator and route through registry
- Models use Pydantic v2 with strict typing
- Async throughout (asyncio)

## Commands
- `pip install -e ".[dev]"` - Install with dev deps
- `python -m finance_agent` - Run the agent
- `pytest` - Run tests
- `ruff check src/` - Lint
- `mypy src/` - Type check
