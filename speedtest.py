import csv
import json
import subprocess
from pathlib import Path

from config import parseConfig
from util import runInShell

BPS_IN_MBPS = 125000

def runSpeedtest(filename: Path):
    response = runInShell('speedtest --accept-license --accept-gdpr --format json')
    data = json.loads(response)

    results = {
        'time': data['timestamp'],
        'down': data['download']['bandwidth'] / BPS_IN_MBPS,
        'up': data['upload']['bandwidth'] / BPS_IN_MBPS,
        'ping': data['ping']['latency'],
    }
    
    header = None if filename.is_file() else results.keys()

    with filename.open('a') as file:
        writer = csv.writer(file)

        if header:
            writer.writerow(header)
        
        writer.writerow(results.values())


if __name__ == '__main__':
    print('Running speedtest...')

    config = parseConfig()
    runSpeedtest(config.resultsCsvPath)

    print(f'Results written to {config.resultsCsvPath}')
