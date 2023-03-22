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

        # Cerca il file "valuesdoc" nel tuo Google Drive
        results = service.files().list(q="name='valuesdoc' and mimeType='application/vnd.google-apps.spreadsheet'",
            pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            print('File "valuesdoc" non trovato.')
            return

        target_file = items[0]
        spreadsheet_id = target_file['id']
        sheet_name = 'Sheet1'
        row_values = ['esempio prova ']
        append_row_to_sheet(sheets_service, spreadsheet_id, sheet_name, row_values)
        print(f"Riga aggiunta al foglio '{sheet_name}' nel file '{target_file['name']}' (ID: {spreadsheet_id})")

    except HttpError as error:
        print(f'An error occurred: {error}')

if __name__ == '__main__':
    main()
