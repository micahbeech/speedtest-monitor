import json
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

SCRIPT_DIR = Path(__file__).parent

@dataclass
class Config:
    deliveryEmail: str
    resultsCsvPath: Path
    summaryHtmlPath: Path

def parseConfig() -> Config:
    configFile = SCRIPT_DIR / 'config.json'

    with configFile.open() as file:
        config: Config = json.load(file, object_hook=lambda x : Config(*x.values()))

    if not config.resultsCsvPath:
        raise ValueError('Missing required value resultsCsvPath!')

    config.resultsCsvPath = Path(config.resultsCsvPath)
    config.summaryHtmlPath = Path(config.summaryHtmlPath)

    return config

if __name__ == '__main__':
    pprint(parseConfig())
