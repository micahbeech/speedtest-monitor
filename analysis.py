from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pprint import pprint
from uuid import uuid4

import matplotlib.pyplot as plt
import pandas as pd

from config import parseConfig


@dataclass
class SpeedData:
    averageDownloadBandwidth: float
    averageUploadBandwidth: float
    averagePing: float
    startDate: datetime
    endDate: datetime
    plotFile: Path

def generateGraphs(data: pd.DataFrame) -> Path:
    axes = data.plot.line(x='time', subplots=[('down', 'up')], figsize=(6,8), grid=True)

    axes[0].set_ylabel('Bandwidth (Mbps)')
    axes[1].set_ylabel('Latency (ms)')
    axes[1].set_xlabel('Time', labelpad=15)

    fig = plt.gcf()
    fig.autofmt_xdate(rotation=45)
    fig.subplots_adjust(bottom=0.25, left=0.25)

    imagePath = Path(__file__).parent / f'results_{uuid4()}.png'
    plt.savefig(imagePath)

    return imagePath

def analyzeData(filepath: Path) -> SpeedData:
    data = pd.read_csv(filepath)

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

if __name__ == '__main__':
    config = parseConfig()

    print(f'Analyzing {config.resultsFile}:')
    data = analyzeData(config.resultsFile)
    pprint(data)

    data.plotFile.unlink()
