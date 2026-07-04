from rich.console import Console
from rich.table import Table

from promptleak.domain.entities import ScanReport
from promptleak.domain.value_objects import Score

_SEVERITY_COLORS = {
    "INFO": "dim",
    "LOW": "cyan",
    "MEDIUM": "yellow",
    "HIGH": "orange3",
    "CRITICAL": "bold red",
}


def render_report(report: ScanReport, score: Score, console: Console | None = None) -> None:
    console = console or Console()

    console.print(f"\n[bold]Cible :[/bold] {report.target_name}")
    console.print(f"[bold]Score :[/bold] {score.value}/100 (note [bold]{score.grade}[/bold])\n")

    if not report.findings:
        console.print("[green]Aucune injection détectée.[/green]")
        return

    table = Table(title="Findings")
    table.add_column("Outil")
    table.add_column("Vecteur")
    table.add_column("Technique")
    table.add_column("Sévérité")
    table.add_column("Preuve")

    for finding in report.findings:
        severity_name = finding.severity.name
        color = _SEVERITY_COLORS.get(severity_name, "white")
        table.add_row(
            finding.tool_name,
            finding.vector.value,
            finding.technique,
            f"[{color}]{severity_name}[/{color}]",
            finding.evidence.excerpt[:60],
        )

    console.print(table)
