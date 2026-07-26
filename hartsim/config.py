import os
from dataclasses import dataclass, field


def _default_port() -> str:
    """Serial port name: HARTSIM_PORT env var overrides the default."""
    return os.environ.get("HARTSIM_PORT", "COM2")


@dataclass
class Configuration:
    port: str = field(default_factory=_default_port)
