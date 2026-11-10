import argparse
import sys
import tomllib
from . import __version__
from .config import config_path, load, save
from .contracts import render, sanitize

# Exit codes: success 0, operational error 1, usage/config error 2, partial 3.
def main(argv=None):
    parser = argparse.ArgumentParser(prog="soral", description="Experimental offline Soral foundation; no HTTP commands yet.")
    parser.add_argument("--version", action="version", version=f"soral {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    version = sub.add_parser("version", help="show version")
    version.add_argument("--format", choices=("text", "json", "jsonl"), default="text")
    config = sub.add_parser("config", help="manage local configuration")
    actions = config.add_subparsers(dest="action", required=True)
    show = actions.add_parser("show")
    show.add_argument("--format", choices=("text", "json", "jsonl"), default="text")
    set_parser = actions.add_parser("set")
    set_parser.add_argument("key", choices=("warning",))
    set_parser.add_argument("value", choices=("true", "false"))
    args = parser.parse_args(argv)
    try:
        if args.command == "version":
            data = {"version": __version__, "schema_version": "1"}
            print(f"soral {__version__}" if args.format == "text" else render(data, args.format))
        elif args.action == "show":
            data = load(config_path())
            print(f"warning = {str(data['warning']).lower()}" if args.format == "text" else render(data, args.format))
        else:
            path = config_path()
            data = load(path)
            data[args.key] = args.value == "true"
            save(path, data)
    except (OSError, ValueError, tomllib.TOMLDecodeError) as exc:
        print(f"soral: {sanitize(str(exc))}", file=sys.stderr)
        return 2
    return 0
