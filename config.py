import json
from dataclasses import dataclass
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

@dataclass
class Config:
    deliveryEmail: str
    resultsFile: Path

def parseConfig() -> Config:
    configFile = SCRIPT_DIR / 'config.json'

    with configFile.open() as config:
        config = json.load(config, object_hook=lambda x : Config(*x.values()))

    resultsFilepath = Path(config.resultsFile)
    config.resultsFile = resultsFilepath if resultsFilepath.is_absolute() else SCRIPT_DIR / resultsFilepath

    return config

if __name__ == '__main__':
    print(parseConfig())
