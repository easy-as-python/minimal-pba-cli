from rich.console import Console

from minimal_pba_cli.plugin import get_latest_version, run_external_subprocess


def upgrade():
    """Install the latest version of this tool."""

    console = Console()
    installed_version, latest_version, _ = get_latest_version("minimal-pba-cli")

    if installed_version == latest_version:
        console.print(f"\n[green]Already on latest version {installed_version}.[/green]")
        return

    run_external_subprocess(
        [
            "pipx",
            "runpip",
            "minimal-pba-cli",
            "install",
            f"minimal-pba-cli=={latest_version}",
            "--force",
        ]
    )
    console.print("\n[green]Upgrade complete.[/green]\n\n")
