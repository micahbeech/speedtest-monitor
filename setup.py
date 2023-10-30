import json
import webbrowser
from pathlib import Path
from shutil import which

from crontab import CronTab

import gmail
from config import Config
from util import runInShell

WORKING_DIRECTORY = Path(__file__).parent
MAIN_FILE = WORKING_DIRECTORY / 'main.py'
CONFIG_FILE = WORKING_DIRECTORY / 'config.json'

CRON = CronTab(user=True)

def installSpeedtestCLI():
    try:
        if which('speedtest'):
            print('Speedtest CLI already installed!')
            print()
            return
        
        print('Attempting to install speedtest CLI...')

        if which('brew'):
            runInShell('brew tap teamookla/speedtest')
            runInShell('brew update')
            runInShell('brew install speedtest --force')

        elif which('apt-get'):
            runInShell('sudo apt-get install curl')
            runInShell('curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash')
            runInShell('sudo apt-get install speedtest')

        elif which('yum'):
            runInShell('curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.rpm.sh | sudo bash')
            runInShell('sudo yum install speedtest')

        else:
            raise AssertionError
        
        print(f'Success! Path to executable: {which("speedtest")}')
        print()
    
    except Exception:
        print('Unable to auto-install the speedtest CLI. Please install it manually before re-running this setup.')

        link = 'https://www.speedtest.net/apps/cli'
        print(f'{link}\n')
        webbrowser.open(link)

        raise


def installCronJob(humanAction: str, machineAction: str, defaultFrequency: int, unit: str):
    print(f'How often (in {unit}) should {humanAction} (default {defaultFrequency})?')
    frequency = input(f'Press enter for default: ') or defaultFrequency

    command = f'python {MAIN_FILE} {machineAction}'
    CRON.remove_all(command=command)
    job = CRON.new(command=command)
    getattr(job.every(frequency), unit)()

def readFilename(type: str, default: str) -> Path:
    print(f'Where would you like {type} to be stored?')
    print('A relative path will be stored in the script directory.')
    print('Provide an absolute path to store the results elsewhere.')

    file = input(f'Press enter for default ("{default}"): ') or default
    return Path(file).expanduser().resolve()

def check(query: str) -> bool:
    return input(f'{query} (y/n) ').lower().strip() == 'y'

def setup():
    installSpeedtestCLI()

    if CONFIG_FILE.is_file() and not check(f'{CONFIG_FILE} already exists. Do you want to overwrite it?'):
        return
    
    print()

    infile = readFilename('speedtest results', 'results.csv')
    installCronJob('speed tests be run', 'test', 1, 'hours')

    print()

    email = outfile = ''
    if check('Would you like results to be emailed to you?'):
        email = input('What email address should the reports be sent to? ')
        installCronJob('speed reports be emailed out', 'mail', 7, 'day')

        print(f'A test email will be sent to {email}')
        print('You may have to authorize the application to send emails on your behalf for this to work.')
        gmail.send(
            to=email,
            subject='Speedtest Monitor Setup',
            html='<p>Success! You have successfully setup email delivery.</p>',
        )

    elif check('Would you like results to be saved to a file?'):
        outfile = readFilename('summary reports', 'summary.html')
        installCronJob('speed reports be generated', 'save', 7, 'day')

    else:
        print('Warning: no analysis setup!')
        print(f'Raw data will still be written to {infile}.')

    print()

    config = Config(deliveryEmail=email, resultsCsvPath=infile, summaryHtmlPath=outfile)
    with CONFIG_FILE.open('w') as configFile:
        json.dump(config.__dict__, configFile, indent=4, default=lambda x : f'{x}')

    print('Installing crontab.')
    print('You may need to grant the script permission to administer your computer.')
    print()
    CRON.write()

    print('Setup complete!')
    print(f'You may edit the configuration by re-running this script, or by modifying {CONFIG_FILE} directly.')

if __name__ == '__main__':
    setup()
