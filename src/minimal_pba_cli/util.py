import subprocess

import typer


def run_external_subprocess(args: list[str]) -> subprocess.CompletedProcess:
    """Run an external subprocess and return the result."""

    result = subprocess.run(args, capture_output=True, encoding="utf-8")

    if result.stdout:
        typer.echo(result.stdout)

    if result.stderr:
        typer.echo(result.stderr, err=True)

    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)

    return result



