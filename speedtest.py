import subprocess
import json
from pathlib import Path
import csv

BPS_IN_MBPS = 125000

def exec(command: str) -> str:
    return subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout

def runSpeedtest(filename: Path):
    response = exec('speedtest --accept-license --accept-gdpr --format json')
    data = json.loads(response)

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

    filename = 'results.csv'
    runSpeedtest(filename)

    print(f'Results written to {filename}')
