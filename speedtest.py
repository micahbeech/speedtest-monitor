import subprocess
import json
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from argparse import ArgumentParser
import csv

RESULTS_PATH = Path(__file__).parent / 'results.csv'
BPS_IN_MBPS = 125000

def exec(command: str) -> str:
    return subprocess.run(command, shell=True, check=True, capture_output=True, text=True).stdout

def runSpeedtest():
    response = exec('speedtest --accept-license --accept-gdpr --format json')
    data = json.loads(response)

    results = {
        'time': data['timestamp'],
        'down': data['download']['bandwidth'] / BPS_IN_MBPS,
        'up': data['upload']['bandwidth'] / BPS_IN_MBPS,
        'ping': data['ping']['latency'],
    }
    
    header = None if RESULTS_PATH.is_file() else results.keys()

    with open(RESULTS_PATH.resolve(), 'a') as file:
        writer = csv.writer(file)

        if header:
            writer.writerow(header)
        
        writer.writerow(results.values())

def generateGraphs(data: pd.DataFrame):
    axes = data.plot.line(x='time', subplots=[('down', 'up')], figsize=(6,8), grid=True)
    axes[0].set_ylabel('Bandwidth (Mbps)')
    axes[1].set_ylabel('Latency (ms)')
    axes[1].set_xlabel('Time', labelpad=15)

    fig = plt.gcf()
    fig.autofmt_xdate(rotation=45)
    fig.subplots_adjust(bottom=0.25, left=0.25)
    plt.show()

def analyzeData():
    data = pd.read_csv(RESULTS_PATH.resolve())

    generateGraphs(data)

    print(data.mean())

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('command', choices=['test', 'graph'])

    args = parser.parse_args()

    match args.command:
        case 'test':
            runSpeedtest()
        case 'analyze':
            analyzeData()
