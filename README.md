# Minimal command-line interface using a plugin-based architecture

This project demonstrates a minimal (but featureful) command-line interface (CLI) using a plugin-based architecture (PBA).
The CLI itself is constructed using [Typer](https://typer.tiangolo.com).

The PBA is achieved using a combination of:

- [pipx](https://pypa.github.io/pipx/)
- [importlib](https://docs.python.org/3/library/importlib.html)
- [packaging](https://packaging.pypa.io/)
- [Libraries.io](https://libraries.io/)

For a working plugin example, see [minimal-pba-cli-plugin-example](https://github.com/easy-as-python/minimal-pba-cli-plugin-example).

## Installation

Install the core CLI using the following command:

```shell
$ pipx install minimal-pba-cli
```

## Usage

List available commands using the help:

```shell
$ pba-cli --help
```

### Plugins

List available plugins using the following command (requires a Libraries.io API key):

```shell
LIBRARIES_IO_API_KEY=<your API key> pba-cli plugin catalog
```

Install a plugin using the following command:

```shell
$ pba-cli plugin install <plugin name>
```

List installed plugins using the following command:

```shell
$ pba-cli plugin list
```

Install a plugin from a local directory using the following command:

```shell
$ pba-cli plugin install-local <path to plugin directory>
```

Uninstall a plugin using the following command:

```shell
$ pba-cli plugin uninstall <plugin name>
```
