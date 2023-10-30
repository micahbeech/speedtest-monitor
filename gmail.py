import mimetypes
from base64 import urlsafe_b64encode
from email.message import EmailMessage
from pathlib import Path
from typing import List

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Ref:
#   - https://developers.google.com/gmail/api/quickstart/python#set_up_your_environment
#   - https://developers.google.com/gmail/api/guides/sending#python

# If modifying these scopes, delete the token file.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
]

SCRIPT_DIR = Path(__file__).parent
TOKEN_FILE = SCRIPT_DIR / 'gmail-token.json'
CREDENTIAL_FILE = SCRIPT_DIR / 'gmail-credentials.json'

def getCredentials() -> Credentials:
    '''
    Fetch, refresh, or generate OAuth credentials for gmail.

    If gmail-token.json contains credentials, they are returned or refreshed if needed.
    Otherwise, new credentials will be generated based on gmail-credentials.json and saved (requires a browser).
    '''
    credentials = None

    if TOKEN_FILE.is_file():
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIAL_FILE, SCOPES)
            credentials = flow.run_local_server(port=0, authorization_prompt_message=None)
        
        with TOKEN_FILE.open('w') as token:
            token.write(credentials.to_json())

    return credentials

def send(to: str, subject: str, html: str, attachments: List[Path] = []):
    '''
    Sends an email to the specified address with subject and body from the authorized email address.
    '''
    service = build('gmail', 'v1', credentials=getCredentials())
    user = service.users().getProfile(userId='me').execute()

    message = EmailMessage()

    message.set_content(html, 'html')

    message['To'] = to
    message['From'] = user['emailAddress']
    message['Subject'] = subject

    for attachment in attachments:
        type_subtype, _ = mimetypes.guess_type(attachment)
        maintype, subtype = type_subtype.split('/')

        with attachment.open('rb') as fp:
            attachment_data = fp.read()
        
        message.add_attachment(attachment_data, maintype, subtype)

    encoded_message = urlsafe_b64encode(message.as_bytes()).decode()
    create_message = {'raw': encoded_message}
    service.users().messages().send(userId='me', body=create_message).execute()


if __name__ == '__main__':
    print('Refreshing gmail credentials if needed...')
    getCredentials()
    print(f'Done. See {TOKEN_FILE}')
