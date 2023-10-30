from argparse import ArgumentParser
from time import sleep

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

    data.plotFile.unlink()

def saveLocally(data: SpeedData):
    outfile = data.plotFile.with_suffix('.html')

    html = generateSummaryHTML(data)
    html += f'<img src="{data.plotFile}"/>'

    with outfile.open('w') as file:
        file.write(html)

    return outfile

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('command', choices=['test', 'save', 'mail'])

    config = parseConfig()
    args = parser.parse_args()

    match args.command:
        case 'test':
            runSpeedtest(config.resultsFile)

        case 'save':
            data = analyzeData(config.resultsFile)
            outfile = saveLocally(data)

            openFile(outfile)

            sleep(1) # so browser opens files before they get deleted

            data.plotFile.unlink()
            outfile.unlink()

        case 'mail':
            data = analyzeData(config.resultsFile)
            notify(data, config.deliveryEmail)
