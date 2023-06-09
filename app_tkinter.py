import tkinter as tk
import tkinter.ttk as ttk
import os
import pickle
import gspread
from tkinter import *
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from tkinter import messagebox
from datetime import datetime


SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
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

class MyApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('INTERFACE PROJECT')
        
        # Impostiamo le dimensioni della finestra larga 2/3
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        screen_width = int(screen_width * 2 / 3)
        self.master.geometry(f"{screen_width}x{screen_height}")
        self.master.resizable(True, True) #utente adatta le dimensioni
        self.initUI()

    def initUI(self):
        font = ('TkDefaultFont', 15)
        #nome
        tk.Label(self.master, text='Nome:', font=font, anchor='w').pack(fill=tk.X, padx=10, pady=10)
        self.input1 = tk.Entry(self.master, font=font)
        self.input1.pack(fill=tk.X, padx=10, pady=10)
        #cognome
        tk.Label(self.master, text='Cognome:', font=font, anchor='w').pack(fill=tk.X, padx=10, pady=10)
        self.input2 = tk.Entry(self.master, font=font)
        self.input2.pack(fill=tk.X, padx=10, pady=10)
        #età
        tk.Label(self.master, text='Età:', font=font, anchor='w').pack(fill=tk.X, padx=10, pady=10)
        self.input3 = tk.Entry(self.master, font=font)
        self.input3.pack(fill=tk.X, padx=10, pady=10)
        #Salva
        tk.Button(self.master, text='Salva', font=font, command=self.salva_dati, width=15).pack(fill=tk.X, padx=10, pady=10)
        #text box
        self.textbox = tk.Text(self.master, font=('TkDefaultFont', 18), state='disabled', wrap='none', height=10)
        self.textbox.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)
        #scroll bar
        scrollbar = tk.Scrollbar(self.master, command=self.textbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.textbox.configure(yscrollcommand=scrollbar.set)

        ttk.Separator(self.master, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)

        # pulsante 
        tk.Button(self.master, text='Aggiorna dati', font=font, command=self.update_data, width=15).pack(fill=tk.X, padx=10, pady=10)

        # eventi
        self.input3.bind('<Return>', lambda event: self.salva_dati()) #invio
        self.input1.focus_set()#focus inizio
        self.input1.icursor(tk.END)#cursor

        # tema
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TLabel', font=font, padding=10)
        style.configure('TEntry', font=font, padding=10)
        style.configure('TButton', font=font, padding=10)

        tk.Label(self.master, text='APPLICAZIONE DI PROVA, KEEP IN TOUCH :P', font=('TkDefaultFont', 28)).pack(fill=tk.X, padx=10, pady=10)
        self.update_data()


    def update_data(self):
        #  Google Sheet
        gs = gspread.authorize(creds)
        sheet = gs.open_by_key(SAMPLE_SPREADSHEET_ID_input).sheet1
        data = sheet.get_all_values()

        # Creo dati 
        text = ''
        for row in data:
            text += '\t'.join(row) + '\n'

        # casella di testo
        self.textbox.config(state='normal')
        self.textbox.delete('1.0', tk.END)
        self.textbox.insert(tk.END, text)
        self.textbox.config(state='disabled')
        

    def salva_dati(self):
        nome = self.input1.get().strip()
        cognome = self.input2.get().strip()
        eta = self.input3.get().strip()
        if nome and cognome and eta:
            data_to_write = [[nome, cognome, eta]]
            body = {'values': data_to_write}
            result = service.spreadsheets().values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID_input, range='A:C',
                                                            valueInputOption='RAW', body=body).execute()
            num_celle_aggiunte = result.get("updates").get("updatedCells")
            if num_celle_aggiunte > 0:
                self.input1.delete(0, tk.END)
                self.input2.delete(0, tk.END)
                self.input3.delete(0, tk.END)
                self.input1.focus_set()
                self.input1.icursor(tk.END)
                self.update_data()
                tk.messagebox.showinfo('Successo', 'Dati salvati correttamente.')
            else:
                tk.messagebox.showerror('Errore', 'Errore durante il salvataggio dei dati.')
        else:
            tk.messagebox.showerror('Errore', 'Inserisci tutti i dati per proseguire.')


if __name__ == '__main__':
    root = tk.Tk()#creo root
    ex = MyApp(root)#creo istanza
    root.mainloop() #avvio ciclo