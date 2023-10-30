from argparse import ArgumentParser
from pathlib import Path

import gmail
from analysis import SpeedData, analyzeData
from config import parseConfig
from speedtest import runSpeedtest
from util import openFile


def generateSummaryHTML(data: SpeedData) -> str:
    return f'''
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

def notify(data: SpeedData, email: str):
    startDate = data.startDate.date()
    endDate = data.endDate.date()

    subject = f'Internet Speed Summary for {startDate}'
    subject += '' if startDate == endDate else f' to {endDate}'

    gmail.send(email, subject, generateSummaryHTML(data), attachments=[data.plotFile])

def saveLocally(data: SpeedData, outfile: Path):
    html = generateSummaryHTML(data)
    html += f'<img src="{data.plotFile}"/>'

    with outfile.open('w') as file:
        file.write(html)


if __name__ == '__main__':
    parser = ArgumentParser(prog='Speedtest Monitor')
    parser.add_argument('command', choices=['test', 'save', 'mail'], help='Command to run')
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

        case 'save':
            if not config.summaryHtmlPath.is_absolute():
                raise ValueError('Please input an absolute path for the summaryHtmlPath to disambiguate file location!')

            data = analyzeData(config.resultsCsvPath)
            saveLocally(data, config.summaryHtmlPath)

            if args.open:
                openFile(config.summaryHtmlPath)

        case 'mail':
            if not config.deliveryEmail:
                raise ValueError('Configuration missing address for email delivery!')
            
            data = analyzeData(config.resultsCsvPath)
            notify(data, config.deliveryEmail)

            data.plotFile.unlink()
