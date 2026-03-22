"""Factory de config — leitura/escrita do .env."""

import os
from pathlib import Path

ENV_PATH = Path(__file__).parent.parent / ".env"


def read_env() -> dict[str, str]:
    if not ENV_PATH.exists():
        return {}
    result = {}
    for line in ENV_PATH.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        result[key.strip()] = value.strip()
    return result


def write_env(data: dict[str, str]) -> None:
    lines = [f"{k}={v}" for k, v in data.items()]
    ENV_PATH.write_text("\n".join(lines) + "\n")


def update_key(env: dict[str, str], key: str, value: str | None) -> None:
    """Atualiza chave no dict e no os.environ se valor não for None."""
    if value is not None:
        env[key] = value
        os.environ[key] = value
