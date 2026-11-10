"""Minimal persistent configuration, using TOML and atomic replacement."""
import os
from pathlib import Path
import tempfile
import tomllib

DEFAULTS = {"warning": True}

def config_path() -> Path:
    base = os.environ.get("SORAL_CONFIG_HOME") or os.environ.get("XDG_CONFIG_HOME")
    return (Path(base) if base else Path.home() / ".config") / "soral" / "config.toml"

def load(path: Path) -> dict:
    if path.is_symlink():
        raise ValueError("configuration file must not be a symlink")
    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return DEFAULTS.copy()
    if set(data) - DEFAULTS.keys() or any(type(v) is not bool for v in data.values()):
        raise ValueError("configuration supports only boolean warning")
    return DEFAULTS | data

def save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink() or path.parent.is_symlink():
        raise ValueError("configuration path must not be a symlink")
    fd, name = tempfile.mkstemp(prefix=".soral-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(f"warning = {str(data['warning']).lower()}\n")
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)
