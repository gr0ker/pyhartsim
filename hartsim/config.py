from dataclasses import dataclass


@dataclass
class Configuration:
    port: str = "COM2"
