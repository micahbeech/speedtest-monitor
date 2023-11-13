import json
import re
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
    print(f'How often (in {unit}) should {humanAction}?')
    frequency = input(f'Press enter for default ({defaultFrequency}): ') or defaultFrequency

    command = f'python {MAIN_FILE} {machineAction}'
    CRON.remove_all(command=command)
    job = CRON.new(command=command)
    getattr(job.every(frequency), unit)()

def readFilename(type: str, default: Path) -> Path:
    print(f'Where would you like {type} to be stored?')
    file = input(f'Press enter for default ("{default}"): ')
    filepath = Path(file) if file else default
    return filepath.expanduser().resolve()

def check(query: str) -> bool:
    return input(f'{query} (y/n) ').lower().strip() == 'y'

def setupEmail() -> str:
    credentials = WORKING_DIRECTORY / 'gmail-credentials.json'
    if not credentials.is_file():
        link = 'https://developers.google.com/gmail/api/quickstart/python'
        print('No Gmail credentials found.')
        print('Follow the steps at the link below to setup an OAuth client ID.')
        print(f'Save the credentials in {credentials} and then re-run this script.\n')

        print(f'{link}\n')
        webbrowser.open(link)

        return ''
    
    while True:
        email = input('What email address should the reports be sent to? ')
        validEmailRegex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

        if re.fullmatch(validEmailRegex, email):
            break

        print('Invalid email address. Please try again.')

    print(f'A test email will be sent to {email}.')
    print('You may have to authorize the application to send emails on your behalf for this to work.')
    gmail.send(
        to=email,
        subject='Speedtest Monitor Setup',
        html='<p>Success! You have successfully setup email delivery.</p>',
    )

    # Keep credentials fresh
    command = f'python {WORKING_DIRECTORY / "gmail.py"}'
    CRON.remove_all(command=command)
    job = CRON.new(command=command)
    job.every(1).day()

    return email

def setup():
    installSpeedtestCLI()

    if CONFIG_FILE.is_file() and not check(f'{CONFIG_FILE} already exists. Do you want to overwrite it?'):
        return
    
    print()

    infile = readFilename('speedtest results', WORKING_DIRECTORY / 'results.csv')
    installCronJob('speed tests be run', 'test', 1, 'hours')

    print()

    outfile = readFilename('summary reports', WORKING_DIRECTORY)
    installCronJob('summary reports be generated', 'report', 7, 'days')

    print()

    email = setupEmail() if check('Would you like to setup automated emails (requires configuring a gmail OAuth app)?') else ''

    print()

    config = Config(deliveryEmail=email, resultsCsvPath=infile, reportDir=outfile)
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
