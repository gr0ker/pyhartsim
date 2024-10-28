import json
from dataclasses import dataclass


@dataclass
class Configuration:
    port: str

    @classmethod
    def load(cls, path: str):
        config_file = open(path)
        try:
            config_data = json.load(config_file)
        finally:
            config_file.close()

        return cls(**config_data)

