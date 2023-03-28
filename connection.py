import sys
import os
import pickle
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QFormLayout
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SAMPLE_SPREADSHEET_ID_input = '1ssWRMfTWKkjD-JdC2Vp2r6b9NlMsh7omqNq_bRW-kdw'
SAMPLE_RANGE_NAME = 'A1:AA1000'

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)

service = build('sheets', 'v4', credentials=creds)

class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Inserisci i dati')
        self.setGeometry(300, 300, 300, 100)
        font = QFont()
        font.setPointSize(13)
        self.label1 = QLabel('Nome')
        self.label1.setFont(font)
        self.input1 = QLineEdit()
        self.label2 = QLabel('Cognome')
        self.label2.setFont(font)
        self.input2 = QLineEdit()
        self.label3 = QLabel('Età')
        self.label3.setFont(font)
        self.input3 = QLineEdit()

        self.button = QPushButton('Salva')
        self.button.setFont(font)
        self.button.clicked.connect(self.salva_dati)

        form_layout = QFormLayout()
        form_layout.addRow(self.label1, self.input1)
        form_layout.addRow(self.label2, self.input2)
        form_layout.addRow(self.label3, self.input3)

        vbox = QVBoxLayout()
        vbox.addLayout(form_layout)
        vbox.addWidget(self.button)

        self.setLayout(vbox)
        self.show()

    def salva_dati(self): #attenzione range
        nome= self.input1.text()
        cognome = self.input2.text()
        eta = self.input3.text()
        data_to_write = [[nome, cognome, eta]]
        body = {
            'values': data_to_write
        }
        result = service.spreadsheets().values().append(
            spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range='A:C', valueInputOption='RAW', body=body).execute()
        print(f'Aggiunte {result.get("updates").get("updatedCells")} celle.')

        self.input1.clear()
        self.input2.clear()
        self.input3.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApp()
    sys.exit(app.exec_())
#problemi commit 