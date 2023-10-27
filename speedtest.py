import subprocess
import json
from pprint import pprint
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from argparse import ArgumentParser
import csv
from dataclasses import dataclass
from datetime import datetime
from gmail import sendEmail

SCRIPT_PATH = Path(__file__).parent
RESULTS_CSV_PATH = SCRIPT_PATH / 'results.csv'
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

def generateGraphs(data: pd.DataFrame) -> Path:
    axes = data.plot.line(x='time', subplots=[('down', 'up')], figsize=(6,8), grid=True)

    axes[0].set_ylabel('Bandwidth (Mbps)')
    axes[1].set_ylabel('Latency (ms)')
    axes[1].set_xlabel('Time', labelpad=15)

    fig = plt.gcf()
    fig.autofmt_xdate(rotation=45)
    fig.subplots_adjust(bottom=0.25, left=0.25)

    imagePath = SCRIPT_PATH / 'results.png'
    plt.savefig(imagePath)

    return imagePath

@dataclass
class SpeedData:
    averageDownloadBandwidth: float
    averageUploadBandwidth: float
    averagePing: float
    startDate: datetime
    endDate: datetime
    plotFile: Path

def analyzeData(filename: Path) -> pd.Series:
    data = pd.read_csv(filename)

    plotFile = generateGraphs(data)

    averages = data[['down', 'up', 'ping']].mean()

    dateFormat = '%Y-%m-%dT%H:%M:%SZ'
    startDate = datetime.strptime(data['time'].iloc[0], dateFormat)
    endDate = datetime.strptime(data['time'].iloc[-1], dateFormat)

    return SpeedData(
        averages['down'],
        averages['up'],
        averages['ping'],
        startDate,
        endDate,
        plotFile,
    )

def notify(data: SpeedData):
    startDate = data.startDate.date()
    endDate = data.endDate.date()

    subject = f'Internet Speed Summary for {startDate}'
    subject += '' if startDate == endDate else f' to {endDate}'

    sendEmail(
        to='beechmicah@gmail.com',
        subject=subject,
        body=f'''
        <table>
            <tbody><tr>
                <td>Average download speed:</td>
                <td>{data.averageDownloadBandwidth:.2f} Mbps</td>
            </tr>
            <tr>
                <td>Average upload speed:</td>
                <td>{data.averageUploadBandwidth:.2f} Mbps</td>
            </tr>
            <tr>
                <td>Average ping:</td>
                <td>{data.averagePing:.2f} ms</td>
            </tr>
            </tbody>
        </table>

        <br/>
        ''',
        bodyType='html',
        attachments=[data.plotFile],
    )

    data.plotFile.unlink()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('command', choices=['test', 'analyze', 'email'])

    args = parser.parse_args()

    match args.command:
        case 'test':
            runSpeedtest(RESULTS_CSV_PATH)
        case 'analyze':
            results = analyzeData(RESULTS_CSV_PATH)
            print(results)
            print(type(results.startDate))
        case 'email':
            results = analyzeData(RESULTS_CSV_PATH)
            notify(results)
