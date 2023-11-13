from argparse import ArgumentParser
from pathlib import Path
from uuid import uuid4

import gmail
from analysis import analyzeData
from config import Config, parseConfig
from speedtest import runSpeedtest
from util import openFile


def generateReport(config: Config) -> Path:
    reportId = uuid4()

    basePath = config.reportDir / f'report_{reportId}'
    imagePath = basePath.with_suffix('.png')
    reportPath = basePath.with_suffix('.html')

    data = analyzeData(config.resultsCsvPath, imagePath)

    startDate = data.startDate.date()
    endDate = data.endDate.date()

    header = f'Internet Speed Summary for {startDate}'
    header += '' if startDate == endDate else f' to {endDate}'

    baseHtml = f'''
        <div style="font-family: Arial;">
            <h1>{header}<h1>

            <table style="text-align: left;">
                <tbody>
                    <tr>
                        <th></th>
                        <th>Download (Mbps)</th>
                        <th>Upload (Mbps)</th>
                        <th>Ping (ms)</th>
                    </tr>
                    <tr>
                        <th>Min</th>
                        <td>{data.downloadBandwidth['min']:.2f}</td>
                        <td>{data.uploadBandwidth['min']:.2f}</td>
                        <td>{data.ping['min']:.2f}</td>
                    </tr>
                    <tr>
                        <th>Average</th>
                        <td>{data.downloadBandwidth['mean']:.2f}</td>
                        <td>{data.uploadBandwidth['mean']:.2f}</td>
                        <td>{data.ping['mean']:.2f}</td>
                    </tr>
                    <tr>
                        <th>Max</th>
                        <td>{data.downloadBandwidth['max']:.2f}</td>
                        <td>{data.uploadBandwidth['max']:.2f}</td>
                        <td>{data.ping['max']:.2f}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        '''

    with reportPath.open('w') as file:
        file.write(baseHtml + f'<img src="{imagePath}"/>')

    if config.deliveryEmail:
        gmail.send(config.deliveryEmail, header, baseHtml, attachments=[imagePath])

    newPath = config.reportDir / f'{config.resultsCsvPath.stem}_{reportId}{config.resultsCsvPath.suffix}'
    config.resultsCsvPath.rename(newPath)

    return reportPath


if __name__ == '__main__':
    parser = ArgumentParser(prog='Speedtest Monitor')
    parser.add_argument('command', choices=['test', 'report'], help='Command to run')
    parser.add_argument(
        '-o', '--open',
        action='store_true',
        help='When command is "save", attempt to open the results file using the default program.',
    )

    config = parseConfig()
    args = parser.parse_args()

    match args.command:
        case 'test':
            runSpeedtest(config.resultsCsvPath)

        case 'report':
            path = generateReport(config)
            if args.open:
                openFile(path)
