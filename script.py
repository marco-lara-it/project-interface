import pandas as pd
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import os
import pickle

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# here enter the id of your google sheet
SAMPLE_SPREADSHEET_ID_input = '1ssWRMfTWKkjD-JdC2Vp2r6b9NlMsh7omqNq_bRW-kdw'
SAMPLE_RANGE_NAME = 'A1:AA1000'

def print_sheet_content(values):
    print("Contenuto del foglio di lavoro:")
    for row in values:
        print(row)

def get_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES) # here enter the name of your downloaded JSON file
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_sheet_data(sheet_id, range_name):
    service = build('sheets', 'v4', credentials=get_credentials())
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
    return result.get('values', [])

def write_data_to_sheet(sheet_id, range_name, data):
    service = build('sheets', 'v4', credentials=get_credentials())
    body = {
        'values': data
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name, valueInputOption='RAW', body=body).execute()
    print(f'Aggiornato {result.get("updatedCells")} celle.')

def main():
    # Scrivi i dati nel foglio
    data_to_write = [['Nuovo dato 1'], ['Nuovo dato 8'], ['Nuovo dato 3'], ['Nuovo dato 2'], ['Nuovo dato 2']]
    write_data_to_sheet(SAMPLE_SPREADSHEET_ID_input, 'A1', data_to_write)

    # Recupera i dati dal foglio di lavoro e stampa il contenuto
    values_input = get_sheet_data(SAMPLE_SPREADSHEET_ID_input, SAMPLE_RANGE_NAME)
    if values_input:
        print_sheet_content(values_input)
    else:
        print('No data found.')


if __name__ == '__main__':
    main()
