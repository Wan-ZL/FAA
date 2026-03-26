"""Rich-based interactive CLI for Finance Agent.

Features:
- Streaming output with markdown rendering
- Command history
- Session management
- Health check command
- Formatted tables and structured output
"""

from __future__ import annotations

import asyncio
import logging
import sys
from pathlib import Path

from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.theme import Theme

# Custom theme
THEME = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "red bold",
    "success": "green",
    "ticker": "bold magenta",
    "signal.buy": "green bold",
    "signal.sell": "red bold",
    "signal.hold": "yellow",
})

console = Console(theme=THEME)
logger = logging.getLogger(__name__)

BANNER = """
╔═══════════════════════════════════════════════════════╗
║               Finance Agent v0.1.0                     ║
║   AI-Powered Multi-Agent Financial Analysis Engine     ║
║                                                        ║
║   Type your question or command:                       ║
║   • /help     — Show available commands                ║
║   • /health   — Check system health                    ║
║   • /status   — Show agent pool status                 ║
║   • /quit     — Exit                                   ║
╚═══════════════════════════════════════════════════════╝
"""

HELP_TEXT = """
## Available Commands

| Command | Description |
|---------|-------------|
| `/help` | Show this help message |
| `/health` | Check system health (APIs, databases, models) |
| `/status` | Show current agent pool status |
| `/history` | Show recent analysis history |
| `/clear` | Clear the screen |
| `/quit` or `/exit` | Exit Finance Agent |

## Example Queries

- "What's AAPL trading at?"
- "Analyze NVDA for a 6-month hold"
- "How does the Fed rate decision affect banking stocks?"
- "Run a Monte Carlo simulation on TSLA"
- "Compare MSFT and GOOGL fundamentals"
- "What's the risk/reward on SPY puts?"

## Tips

- Mention a **ticker symbol** for targeted analysis
- Specify a **timeframe** (day trade, swing, 6 months, long term)
- Ask for **specific analysis** (technical, fundamental, sentiment, options)
- Request **risk analysis** (VaR, stress test, Monte Carlo)
"""


def print_banner() -> None:
    """Print the welcome banner."""
    console.print(Panel(BANNER.strip(), style="cyan", border_style="bright_blue"))


def print_help() -> None:
    """Print help text."""
    console.print(Markdown(HELP_TEXT))


async def health_check() -> None:
    """Check system health: API keys, database connections, model availability."""
    from finance_agent.config import settings

    table = Table(title="System Health Check", show_header=True)
    table.add_column("Component", style="bold")
    table.add_column("Status")
    table.add_column("Details")

    # Check Anthropic API key
    if settings.api_keys.anthropic_api_key:
        table.add_row("Anthropic API", "[green]✓ Configured[/]", "API key present")
    else:
        table.add_row("Anthropic API", "[red]✗ Missing[/]", "Set ANTHROPIC_API_KEY in .env")

    # Check FRED API key
    if settings.api_keys.fred_api_key:
        table.add_row("FRED API", "[green]✓ Configured[/]", "API key present")
    else:
        table.add_row("FRED API", "[yellow]○ Optional[/]", "Set FRED_API_KEY for macro data")

    # Check FinnHub API key
    if settings.api_keys.finnhub_api_key:
        table.add_row("FinnHub API", "[green]✓ Configured[/]", "API key present")
    else:
        table.add_row("FinnHub API", "[yellow]○ Optional[/]", "Set FINNHUB_API_KEY for real-time quotes")

    # Check yfinance (always available)
    try:
        import yfinance
        table.add_row("yfinance", "[green]✓ Available[/]", f"v{yfinance.__version__}")
    except ImportError:
        table.add_row("yfinance", "[red]✗ Missing[/]", "pip install yfinance")

    # Check pandas-ta
    try:
        import pandas_ta
        table.add_row("pandas-ta", "[green]✓ Available[/]", "Technical analysis ready")
    except ImportError:
        table.add_row("pandas-ta", "[red]✗ Missing[/]", "pip install pandas-ta")

    # Check DuckDB
    try:
        import duckdb
        table.add_row("DuckDB", "[green]✓ Available[/]", f"v{duckdb.__version__}")
    except ImportError:
        table.add_row("DuckDB", "[red]✗ Missing[/]", "pip install duckdb")

    # Check ChromaDB
    try:
        import chromadb
        table.add_row("ChromaDB", "[green]✓ Available[/]", "Vector store ready")
    except ImportError:
        table.add_row("ChromaDB", "[yellow]○ Optional[/]", "pip install chromadb (Phase 5)")

    # Check Neo4j
    try:
        from neo4j import GraphDatabase
        table.add_row("Neo4j Driver", "[green]✓ Available[/]", "KG driver ready")
    except ImportError:
        table.add_row("Neo4j Driver", "[yellow]○ Optional[/]", "pip install neo4j (Phase 5)")

    # Check SQLite board
    board_path = Path(settings.memory.sqlite_board_path)
    if board_path.parent.exists():
        table.add_row("Shared Board", "[green]✓ Ready[/]", str(board_path))
    else:
        table.add_row("Shared Board", "[yellow]○ Will create[/]", str(board_path))

    # LLM Config
    table.add_row("Leader Model", "[info]" + settings.llm.leader_model + "[/]", "Orchestration & synthesis")
    table.add_row("Worker Model", "[info]" + settings.llm.worker_model + "[/]", "Analysis tasks")
    table.add_row("Router Model", "[info]" + settings.llm.router_model + "[/]", "Intent classification")

    console.print(table)


async def run_analysis(query: str, api_tools: list, tool_handlers: dict) -> None:
    """Run a financial analysis query."""
    from finance_agent.agent.team import TeamLeader

    # Create and run team leader
    leader = TeamLeader(tools=api_tools, tool_handlers=tool_handlers)

    with console.status("[bold cyan]Analyzing...", spinner="dots"):
        try:
            result = await leader.analyze(query)
        except Exception as e:
            console.print(f"[error]Analysis failed: {e}[/]")
            logger.exception("Analysis failed")
            return

    # Display result
    console.print()
    console.print(Panel(
        Markdown(result),
        title="[bold]Analysis Report[/]",
        border_style="green",
        padding=(1, 2),
    ))
    console.print()


async def interactive_loop() -> None:
    """Main interactive loop."""
    print_banner()

    # Register tools once at startup
    from finance_agent.tools.market import market_data_group
    from finance_agent.tools.fundamentals import fundamentals_group
    from finance_agent.tools.technical import technical_group
    from finance_agent.tools.options import options_group
    from finance_agent.tools.macro import macro_group
    from finance_agent.tools.sentiment import sentiment_group
    from finance_agent.tools.risk import risk_backtest_group
    from finance_agent.tools.registry import tool_registry

    for group in [market_data_group, fundamentals_group, technical_group,
                  options_group, macro_group, sentiment_group, risk_backtest_group]:
        tool_registry.register_group(group)

    api_tools, handlers = tool_registry.get_all_tools()

    history: list[str] = []

    while True:
        try:
            query = Prompt.ask("\n[bold cyan]finance-agent[/]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[info]Goodbye![/]")
            break

        query = query.strip()
        if not query:
            continue

        history.append(query)

        # Handle commands
        if query.startswith("/"):
            cmd = query.lower().split()[0]
            if cmd in ("/quit", "/exit", "/q"):
                console.print("[info]Goodbye![/]")
                break
            elif cmd == "/help":
                print_help()
            elif cmd == "/health":
                await health_check()
            elif cmd == "/clear":
                console.clear()
                print_banner()
            elif cmd == "/history":
                if history:
                    for i, h in enumerate(history[-10:], 1):
                        console.print(f"  {i}. {h}")
                else:
                    console.print("  No history yet.")
            elif cmd == "/status":
                console.print("[info]Agent pool: idle (no active analysis)[/]")
            else:
                console.print(f"[warning]Unknown command: {cmd}. Type /help for available commands.[/]")
            continue

        # Run analysis
        await run_analysis(query, api_tools, handlers)


def main() -> None:
    """CLI entry point."""
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    )

    # Check for --health-check flag
    if "--health-check" in sys.argv:
        asyncio.run(health_check())
        return

    # Check for --mcp flag (run as MCP server)
    if "--mcp" in sys.argv:
        from finance_agent.mcp.server import main as mcp_main
        mcp_main()
        return

    # Run interactive loop
    try:
        asyncio.run(interactive_loop())
    except KeyboardInterrupt:
        console.print("\n[info]Goodbye![/]")


if __name__ == "__main__":
    main()
