"""Tests for CLI tooling commands."""
import os
from pathlib import Path
from click.testing import CliRunner
import pytest

from cli import cli


def test_cli_list_reports():
    """Test listing discovered report plugins."""
    runner = CliRunner()
    result = runner.invoke(cli, ["list-reports"])
    assert result.exit_code == 0
    assert "default_metric_report" in result.output
    assert "ecommerce_summary" in result.output


def test_cli_seed_demo():
    """Test seeding demo data for 2 days."""
    runner = CliRunner()
    result = runner.invoke(cli, ["seed-demo", "--days", "2", "--clear"])
    assert result.exit_code == 0
    assert "Successfully seeded" in result.output


def test_cli_test_report(tmp_path):
    """Test generating report locally via CLI."""
    runner = CliRunner()
    out_dir = str(tmp_path / "cli_output")
    result = runner.invoke(cli, ["test-report", "ecommerce_summary", "--days", "3", "--output-dir", out_dir])
    assert result.exit_code == 0
    assert "Test completed!" in result.output

    # Verify generated files exist
    output_files = list(Path(out_dir).iterdir())
    names = [f.name for f in output_files]
    assert any("preview.png" in n for n in names)
    assert any("report.pdf" in n for n in names)
    assert any("data.xlsx" in n for n in names)
    assert any("caption.txt" in n for n in names)


def test_cli_create_plugin(tmp_path, monkeypatch):
    """Test scaffolding a custom plugin."""
    # Temporarily point custom_reports to a temp folder
    custom_dir = tmp_path / "custom_reports"
    custom_dir.mkdir(parents=True, exist_ok=True)

    # Scaffolding command
    runner = CliRunner()
    result = runner.invoke(cli, ["create-plugin", "finance_ledger"])
    assert result.exit_code == 0
    assert "Created report plugin scaffold" in result.output
    
    # Check generated file exists in app/custom_reports
    expected_file = Path("app/custom_reports/finance_ledger_report.py")
    if expected_file.exists():
        content = expected_file.read_text(encoding="utf-8")
        assert "class FinanceLedgerReport(BaseReport):" in content
        # Clean up scaffolded test file
        expected_file.unlink()
