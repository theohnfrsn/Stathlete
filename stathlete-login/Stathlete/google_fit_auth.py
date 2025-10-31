from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Google Fit requires these scopes for reading data
SCOPES = ['https://www.googleapis.com/auth/fitness.activity.read']

def get_fit_service():
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('fitness', 'v1', credentials=creds)
    return service
