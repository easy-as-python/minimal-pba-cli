import atexit
import traceback
import importlib
from typing import Annotated

import requests
import typer
from typer.main import get_group
from trogon import Trogon
from rich.console import Console
from rich.panel import Panel

from minimal_pba_cli.upgrade import upgrade
from minimal_pba_cli.plugin import plugin, find_plugins, get_latest_version
from minimal_pba_cli.customization import list_available_commands, create_command_wrapper


app = typer.Typer()


@app.command()
def hello(name: Annotated[str, typer.Argument()] = "world"):
    """Say hello to NAME."""

    typer.echo(f"Hello, {name}!")


@app.callback(invoke_without_command=True)
def default(context: typer.Context):
    if context.invoked_subcommand is None:
        Trogon(get_group(app), click_context=context).run()


def main():
    _register_plugins(app)
    app.add_typer(plugin, name="plugin", help="Manage plugins.")
    app.command()(upgrade)
    for command, full_path in list_available_commands():
        create_command_wrapper(app, command, full_path)
    app()


def _register_plugins(app: typer.Typer):
    """Register commands from installed packages that provide CLI plugins."""

    console = Console(stderr=True)
    plugins = find_plugins()

    # Import the plugin and add its commands to the app
    for plugin_name, plugin_info in sorted(plugins.items()):
        try:
            plugin_module = importlib.__import__(plugin_info["path"])
            commands = getattr(plugin_module.plugin, "commands", {})
            groups = getattr(plugin_module.plugin, "groups", {})

            for group_name, group in groups.items():
                app.add_typer(group, name=group_name)

            for command in commands.values():
                app.command()(command)
        except Exception:
            console.print(f'\n[red]Failed to load plugin "{plugin_name}". Stack trace:[/red]\n')
            console.print(traceback.format_exc())
            console.print(
                "[red]You can set the [bold cyan]DISABLE_PLUGINS[/bold cyan] environment variable to [bold cyan]true[/bold cyan] to run the CLI without plugins.[/red]"
            )
            console.print(
                "[red]As an example, you can run [bold cyan]DISABLE_PLUGINS=true pba-cli plugin uninstall <plugin>[/bold cyan] to remove a problematic plugin or [bold cyan]DISABLE_PLUGINS=true pba-cli plugin install <plugin>[/bold cyan] to attempt to upgrade a plugin.[/red]\n"
            )
            continue


def _upgrade_check() -> None:
    try:
        current_version, latest_version, is_upgrade = get_latest_version("minimal-pba-cli")
    except requests.exceptions.RequestException:
        typer.secho(
            "Checking for minimal-pba-cli updates failed.",
            fg=typer.colors.YELLOW,
        )
        return

    if is_upgrade:
        console = Console()
        changelog_link = "[link=https://github.com/easy-as-python/minimal-pba-cli/blob/main/CHANGELOG.md]changelog[/link]"
        console.print(
            Panel(
                f""":rocket: Update available!

[yellow]{current_version}[/yellow] -> [bold green]{latest_version}[/bold green] ({changelog_link})

Run [bold]pba-cli upgrade[/bold] to upgrade.""",
                expand=False,
                padding=(1, 10),
            )
        )

atexit.register(_upgrade_check)
