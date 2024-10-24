from dataclasses import dataclass


@dataclass
class Configuration:
    port: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)
