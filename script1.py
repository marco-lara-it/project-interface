from __future__ import print_function

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']

def append_row_to_sheet(service, spreadsheet_id, sheet_name, row_values):
    range_name = 'A1:AA1000'
    body = {
        'values': [row_values]
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', insertDataOption='INSERT_ROWS', body=body).execute()
    return result
def main():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        sheets_service = build('sheets', 'v4', credentials=creds)

        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            print(u'{0} ({1})'.format(item['name'], item['id']))
        first_file = items[0]
        if first_file['mimeType'] == 'application/vnd.google-apps.spreadsheet':
            spreadsheet_id = first_file['id']
            sheet_name = 'Sheet1'
            row_values = ['Questo', 'è', 'un', 'test']
            append_row_to_sheet(sheets_service, spreadsheet_id, sheet_name, row_values)
            print(f"Riga aggiunta al foglio '{sheet_name}' nel file '{first_file['name']}' (ID: {spreadsheet_id})")
        else:
            print("Il primo file nell'elenco non è un foglio di Google Sheet.")

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
