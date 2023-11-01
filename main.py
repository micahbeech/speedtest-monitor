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

    baseHtml = f'''
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
        '''

    with reportPath.open('w') as file:
        file.write(baseHtml + f'<img src="{imagePath}"/>')

    if config.deliveryEmail:
        startDate = data.startDate.date()
        endDate = data.endDate.date()

        subject = f'Internet Speed Summary for {startDate}'
        subject += '' if startDate == endDate else f' to {endDate}'

        gmail.send(config.deliveryEmail, subject, baseHtml, attachments=[imagePath])

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
