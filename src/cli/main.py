"""Main CLI interface for stocklyzer."""

import typer
from rich.console import Console

from .commands.ticker import ticker_command

app = typer.Typer(
    help="Stocklyzer CLI - A command line interface for stock analysis",
    epilog="""
Examples:
  slz ticker AAPL           Show stock information for Apple
  slz --help               Show this help message

For more information, visit: https://github.com/khaino/stocklyzer
    """,
    rich_markup_mode="rich"
)

# Add the ticker command directly
app.command("ticker")(ticker_command)

console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main entry point for stocklyzer CLI.

    Stocklyzer is a command line tool for stock analysis.

    Examples:
        slz ticker AAPL   # Get Apple stock info
        slz --help        # Show help
    """
    if ctx.invoked_subcommand is None:
        # Show welcome message
        console.print("Welcome to Stocklyzer! 🚀")
        console.print("Use --help to see available commands.")
        console.print("\nQuick start:")
        console.print("  slz ticker AAPL  # Get Apple stock info")
        console.print("  slz ticker MSFT  # Get Microsoft stock info")


if __name__ == "__main__":
    app()
