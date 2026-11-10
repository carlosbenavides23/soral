"""Initial result contract; acquisition is not implemented in E1."""
from dataclasses import asdict, dataclass
import json
import unicodedata

SCHEMA_VERSION = "1"

@dataclass(frozen=True)
class ResultError:
    code: str
    message: str

@dataclass(frozen=True)
class TargetResult:
    target: str
    error: ResultError | None = None
    schema_version: str = SCHEMA_VERSION

def sanitize(value: str) -> str:
    return "".join(f"\\u{ord(c):04x}" if unicodedata.category(c) in {"Cc", "Cf", "Cs"} else c for c in value)

def render(data: object, format: str) -> str:
    if format == "text":
        return sanitize(str(data))
    if format not in {"json", "jsonl"}:
        raise ValueError("invalid format")
    return json.dumps(data, ensure_ascii=True, default=lambda value: asdict(value))
