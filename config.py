import json
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

CONFIG_FILE = Path(__file__).parent / 'config.json'

@dataclass
class Config:
    deliveryEmail: str | None
    resultsCsvPath: Path
    reportDir: Path

def parseConfig() -> Config:
    with CONFIG_FILE.open() as file:
        configDict = json.load(file)

    config = Config(
        resultsCsvPath=Path(configDict['resultsCsvPath']),
        reportDir=Path(configDict['reportDir']),
        deliveryEmail=configDict.get('deliveryEmail')
    )

    assert config.resultsCsvPath.is_absolute()
    assert config.reportDir.is_absolute()
    assert config.reportDir.is_dir()

    return config

if __name__ == '__main__':
    pprint(parseConfig())
