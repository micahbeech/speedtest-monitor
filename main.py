from argparse import ArgumentParser

import gmail
from analysis import SpeedData, analyzeData
from config import parseConfig
from speedtest import runSpeedtest


def notify(data: SpeedData, email: str):
    startDate = data.startDate.date()
    endDate = data.endDate.date()

    subject = f'Internet Speed Summary for {startDate}'
    subject += '' if startDate == endDate else f' to {endDate}'

    gmail.send(
        to=email,
        subject=subject,
        html=f'''
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
        attachments=[data.plotFile],
    )

    data.plotFile.unlink()

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('command', choices=['test', 'data', 'mail'])

    config = parseConfig()
    args = parser.parse_args()

    match args.command:
        case 'test':
            runSpeedtest(config.resultsFile)
        case 'data':
            data = analyzeData(config.resultsFile)
            print(data)
        case 'mail':
            data = analyzeData(config.resultsFile)
            notify(data, config.deliveryEmail)
