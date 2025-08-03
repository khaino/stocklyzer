"""Tests for CLI commands."""

from typer.testing import CliRunner

from cli.main import app


class TestCLICommands:
    """Test suite for CLI commands."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_cli_help(self):
        """Test that the main help command works."""
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Stocklyzer CLI" in result.stdout
        assert "ticker" in result.stdout

    def test_cli_main_without_command(self):
        """Test running CLI without any command."""
        result = self.runner.invoke(app, [])
        assert result.exit_code == 0
        assert "Welcome to Stocklyzer!" in result.stdout
        assert "Quick start:" in result.stdout

    def test_ticker_help(self):
        """Test ticker command help."""
        result = self.runner.invoke(app, ["ticker", "--help"])
        assert result.exit_code == 0
        assert "Get comprehensive stock information" in result.stdout
        assert "Examples:" in result.stdout

    def test_ticker_aapl(self):
        """Test ticker command with AAPL."""
        result = self.runner.invoke(app, ["ticker", "AAPL"])
        assert result.exit_code == 0
        assert "AAPL" in result.stdout
        assert "Apple" in result.stdout
        assert "Price:" in result.stdout
        # Real data includes these fields
        assert ("Market Cap" in result.stdout or "P/E Ratio" in result.stdout)

    def test_ticker_msft(self):
        """Test ticker command with MSFT."""
        result = self.runner.invoke(app, ["ticker", "MSFT"])
        assert result.exit_code == 0
        assert "MSFT" in result.stdout
        assert "Microsoft" in result.stdout
        assert "Price:" in result.stdout

    def test_ticker_unknown(self):
        """Test ticker command with unknown ticker."""
        result = self.runner.invoke(app, ["ticker", "ZZZZZ"])
        assert result.exit_code == 0
        assert "ZZZZZ" in result.stdout
        # Should show error message for invalid ticker
        assert "Could not fetch data" in result.stdout

    def test_ticker_invalid_symbol(self):
        """Test ticker command with invalid symbol format."""
        result = self.runner.invoke(app, ["ticker", "TOOLONG123"])
        assert result.exit_code == 0
        assert "Validation Error" in result.stdout
        assert "Invalid symbol format" in result.stdout

    def test_ticker_missing_argument(self):
        """Test ticker command without symbol argument."""
        result = self.runner.invoke(app, ["ticker"])
        assert result.exit_code == 2  # Typer returns 2 for missing required arguments
        # Error messages in typer go to stderr in the output
        assert "Missing argument" in result.output or "Missing argument" in str(result.exception)
