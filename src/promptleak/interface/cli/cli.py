import asyncio

import click

from promptleak.bootstrap import build_scan_use_case
from promptleak.domain.value_objects import McpTargetConfig, Scenario
from promptleak.interface.cli.presenter import render_report


@click.command()
@click.argument("command")
@click.argument("target_args", nargs=-1)
@click.option("--name", default=None, help="Nom de la cible (par défaut : COMMAND).")
@click.option(
    "--dynamic-task",
    "dynamic_tasks",
    multiple=True,
    help=(
        "Tâche confiée à un agent réel pour le test dynamique "
        "(option répétable, appels API facturés)."
    ),
)
def scan(
    command: str, target_args: tuple[str, ...], name: str | None, dynamic_tasks: tuple[str, ...]
) -> None:
    """Scanne un serveur MCP cible : COMMAND [TARGET_ARGS...]."""
    target = McpTargetConfig(name=name or command, command=command, args=target_args)
    scenarios = [
        Scenario(id=f"scenario-{index}", user_task=task)
        for index, task in enumerate(dynamic_tasks, start=1)
    ]

    use_case = build_scan_use_case(with_dynamic_agent=bool(scenarios))
    report, score = asyncio.run(use_case.execute(target, scenarios))

    render_report(report, score)


def main() -> None:
    scan()


if __name__ == "__main__":
    main()
