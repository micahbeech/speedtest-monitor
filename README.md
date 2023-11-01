# Speedtest Monitor

Track your internet speed and visualize the results.

## Installation

### Prerequisites
1. [Python 3.11+](https://www.python.org/about/gettingstarted/)
2. [pip](https://pip.pypa.io/en/stable/)

### Automatic Setup (recommended)

```sh
git clone <REPO>
cd REPO
./setup.sh
```

> Note: The setup script works for Unix users only.
>
> If you are a Windows user,
> or run into issues with the setup script,
> follow the [manual setup steps](#manual-setup) below.

### Manual Setup

1. Clone the source code
    ```sh
    git clone <REPO>
    cd REPO
    ```

2. Install the Python dependencies
    ```sh
    pip install -q -r requirements.txt
    ```

3. Install the Speedtest CLI https://www.speedtest.net/apps/cli

4. Create a configuration file `config.json`
    ```json
    {
        "resultsCsvPath": "/path/to/results.csv",
        "reportDir": "/path/to/output/directory"
    }
    ```

5. Install two cron jobs, one to run speedtests and the other to generate reports. 
For example, this crontab runs speedtests every hour 
and generates a report every 7 days:
    ```
    @hourly python /path/to/speedtest/main.py test
    0 0 */7 * * python /path/to/speedtest/main.py report
    ```

Optionally, you can have reports automatically emailed to you when they are generated. This requires the additional setup steps:

1. Create a Google Cloud project
https://developers.google.com/workspace/guides/create-project
2. Enable access to the Gmail API for that project
https://console.cloud.google.com/apis/enableflow?apiid=gmail.googleapis.com
3. Configure OAuth consent for an external test app. Add your email as a test user
https://console.cloud.google.com/apis/credentials/consent
4. Generate an OAuth client ID and save it in the source directory as `gmail-credentials.json`
https://console.cloud.google.com/apis/credentials
5. Update `config.json` with the following key:
    ```json
    {
        "deliveryEmail": "youremail@example.com"
    }
    ```
6. Run `python gmail.py` to authorize the app to send emails on your behalf.

For more information, see https://developers.google.com/gmail/api/quickstart/python


