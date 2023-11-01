import json
from dataclasses import dataclass
from pathlib import Path
from pprint import pprint

SCRIPT_DIR = Path(__file__).parent

@dataclass
class Config:
    deliveryEmail: str
    resultsCsvPath: Path
    reportDir: Path

def parseConfig() -> Config:
    configFile = SCRIPT_DIR / 'config.json'

    with configFile.open() as file:
        config: Config = json.load(file, object_hook=lambda x : Config(*x.values()))
    
    assert config.resultsCsvPath
    assert config.reportDir

    config.resultsCsvPath = Path(config.resultsCsvPath)
    config.reportDir = Path(config.reportDir)

    assert config.resultsCsvPath.is_absolute()
    assert config.reportDir.is_absolute()
    assert config.reportDir.is_dir()

    return config

if __name__ == '__main__':
    pprint(parseConfig())
