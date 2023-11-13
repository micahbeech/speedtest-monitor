from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from pprint import pprint

import matplotlib.pyplot as plt
import pandas as pd

from config import parseConfig


@dataclass
class SpeedData:
    downloadBandwidth: pd.Series
    uploadBandwidth: pd.Series
    ping: pd.Series
    startDate: datetime
    endDate: datetime

def generateGraphs(data: pd.DataFrame, plotPath: Path):
    axes = data.plot.line(x='time', subplots=[('down', 'up')], figsize=(6,8), grid=True)

    axes[0].set_ylabel('Bandwidth (Mbps)')
    axes[1].set_ylabel('Latency (ms)')
    axes[1].set_xlabel('Time', labelpad=15)

    fig = plt.gcf()
    fig.autofmt_xdate(rotation=45)
    fig.subplots_adjust(bottom=0.25, left=0.25)

    plt.savefig(plotPath)

def analyzeData(csvPath: Path, plotPath: Path) -> SpeedData:
    data = pd.read_csv(csvPath)

    generateGraphs(data, plotPath)

    values = data[['down', 'up', 'ping']].agg(['min', 'mean', 'max'])

    dateFormat = '%Y-%m-%dT%H:%M:%SZ'
    startDate = datetime.strptime(data['time'].iloc[0], dateFormat)
    endDate = datetime.strptime(data['time'].iloc[-1], dateFormat)

    return SpeedData(
        values['down'],
        values['up'],
        values['ping'],
        startDate,
        endDate,
    )

if __name__ == '__main__':
    config = parseConfig()

    print(f'Analyzing {config.resultsCsvPath}:')
    plotFile = config.reportDir / 'sample.png'
    data = analyzeData(config.resultsCsvPath, plotFile)
    pprint(data)

    plotFile.unlink()
