import contextlib
import errno
import os
import sys
from pathlib import Path

import typer


def list_available_commands(prefix: str = "minimal-pba-cli-") -> list[tuple[str, str]]:
    """List all commands available on the PATH that match an optional prefix."""
    commands = []

    for path_str in os.getenv("PATH", "").split(os.pathsep):
        path = Path(path_str)

        with contextlib.suppress(PermissionError):
            if path.is_dir():
                for file in path.iterdir():
                    if file.is_dir():
                        continue

                    if os.access(file, os.X_OK) and file.name.startswith(prefix):
                        commands.append((file.name, str(file)))
    return sorted(set(commands))


def create_command_wrapper(cli: typer.Typer, command: str, full_path: str):
    cli_command_name = command.replace("minimal-pba-cli-", "")

    def typer_wrapper_command():
        commands = [command, *sys.argv[2:]]
        command_string = " ".join(commands)
        display = typer.style(command_string, fg=typer.colors.CYAN, bold=True)
        typer.echo(f"Running {display}", err=True)

        try:
            os.execlp(command, *commands)
        except OSError as e:
            if e.errno == errno.ENOEXEC:
                typer.secho(f"Command {command} found, but does not specify a handler. Try adding a shebang line to the file.", fg=typer.colors.RED, err=True)

    typer_wrapper_command.__doc__ = f"({full_path}): Custom command with unknown options. Try `pba-cli {cli_command_name} -- --help` for more information."

    cli.command(
        name=cli_command_name,
        context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
    )(typer_wrapper_command)
