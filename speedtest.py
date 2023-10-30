import csv
import json
import subprocess
from pathlib import Path

from config import parseConfig

BPS_IN_MBPS = 125000

def runSpeedtest(filename: Path):
    command = 'speedtest --accept-license --accept-gdpr --format json'
    response = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    data = json.loads(response.stdout)

    results = {
        'time': data['timestamp'],
        'down': data['download']['bandwidth'] / BPS_IN_MBPS,
        'up': data['upload']['bandwidth'] / BPS_IN_MBPS,
        'ping': data['ping']['latency'],
    }
    
    header = None if filename.is_file() else results.keys()

    with open(filename, 'a') as file:
        writer = csv.writer(file)

        if header:
            writer.writerow(header)
        
        writer.writerow(results.values())


if __name__ == '__main__':
    print('Running speedtest...')

    config = parseConfig()
    runSpeedtest(config.resultsFile)

    print(f'Results written to {config.resultsFile}')
