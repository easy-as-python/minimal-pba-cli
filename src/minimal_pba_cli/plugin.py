import importlib.metadata
import subprocess
from pathlib import Path
from typing import Annotated
from importlib.metadata import PackageNotFoundError, version

import requests
import typer
from packaging.version import Version
from requests.exceptions import HTTPError
from rich.console import Console
from rich.table import Table


plugin = typer.Typer()


@plugin.command(name="list")
def list_plugins():
    """List installed plugins."""

    console = Console()
    table = Table("Name", "Version", title="Installed CLI plugins", min_width=50, highlight=True)

    for name, plugin_info in sorted(find_plugins().items(), key=lambda x: x[0]):
        table.add_row(name, plugin_info["version"])

    if table.rows:
        print()
        console.print(table)
    else:
        typer.secho("No plugins installed.", fg=typer.colors.BRIGHT_BLACK)


@plugin.command()
def install(
    name: Annotated[
        str,
        typer.Argument(
            help="Name of the plugin to install, excluding the `minimal-pba-cli-plugin-` prefix."
        ),
    ],
):
    """Install a published plugin."""

    installed_plugins = find_plugins()
    already_installed = name in installed_plugins
    version_to_install: str | Version | None = None
    upgrade = False

    if already_installed:
        typer.secho(f"Plugin '{name}' is already installed.", fg=typer.colors.BRIGHT_YELLOW)
        upgrade = typer.confirm("Do you want to upgrade to the latest version?")

    if already_installed and not upgrade:
        typer.confirm("Do you want to reinstall the plugin at its current version?", abort=True)
        version_to_install = installed_plugins[name]["version"]

    if not already_installed or upgrade:
        try:
            _, version_to_install, _ = _get_latest_version(f"minimal-pba-cli-plugin-{name}")
        except HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                raise typer.BadParameter(
                    f"Plugin '{name}' not found."
                ) from None

    typer.echo(f"Installing plugin '{name}' version '{version_to_install}'...")

    args = [
        "pipx",
        "inject",
        "minimal-pba-cli",
        f"minimal-pba-cli-plugin-{name}=={version_to_install}",
    ]
    if already_installed:
        args.append("--force")

    _run_external_subprocess(args)


@plugin.command()
def install_local(path: Annotated[Path, typer.Argument(help="Path to the plugin directory.")]):
    """Install a local plugin."""

    typer.echo(f"Installing plugin from '{path}'...")
    _run_external_subprocess([
        "pipx",
        "inject",
        "--editable",
        "--force",
        "minimal-pba-cli",
        str(path),
    ])


@plugin.command()
def uninstall(name: Annotated[str, typer.Argument(help="Name of the plugin to uninstall, excluding the `minimal-pba-cli-plugin-` prefix.")]):
    """Uninstall a plugin."""

    typer.echo(f"Uninstalling plugin '{name}'...")
    _run_external_subprocess([
        "pipx",
        "uninject",
        "minimal-pba-cli",
        f"minimal-pba-cli-plugin-{name}",
    ])


def _get_installed_version(name: str) -> Version | None:
    """Determine the currently-installed version of the specified package."""

    try:
        return Version(version(name))
    except PackageNotFoundError:
        return None


def _get_latest_version(name: str) -> tuple[Version | None, Version, bool]:
    """Get the latest published version of a package."""

    url = f"https://pypi.org/pypi/{name}/json"
    response = requests.get(url)

    data = response.json()
    latest = Version(data["info"]["version"])
    current = _get_installed_version(name)
    return current, latest, current < latest if current else True


def find_plugins() -> dict[str, dict[str, str]]:
    """Discover installed packages that provide CLI plugins."""

    plugins = {}

    for installed_package in importlib.metadata.distributions():
        for entry_point in installed_package.entry_points:
            if entry_point.group == "minimal_pba_cli":
                plugins[entry_point.name] = {
                    "path": entry_point.value,
                    "version": installed_package.version,
                }

    return plugins


def _run_external_subprocess(args: list[str]) -> subprocess.CompletedProcess:
    """Run an external subprocess and return the result."""

    result = subprocess.run(args, capture_output=True, encoding="utf-8")

    if result.stdout:
        typer.echo(result.stdout)

    if result.stderr:
        typer.echo(result.stderr, err=True)

    if result.returncode != 0:
        raise typer.Exit(code=result.returncode)

    return result
