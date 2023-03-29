import tkinter as tk
import tkinter.ttk as ttk
import os
import pickle
import gspread
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from tkinter import messagebox

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
        self.master.title('Inserisci i dati')
        
        # Impostiamo le dimensioni della finestra come la metà dello schermo
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        self.master.geometry(f"{screen_width//2}x{screen_height}")#cambiare
        self.master.resizable(True, True) #adattare le dimensioni
        self.initUI()

    def initUI(self):
        font = ('TkDefaultFont', 13)

        tk.Label(self.master, text='Nome:', font=font).grid(row=0, column=0, sticky='w', padx=10, pady=10)
        self.input1 = tk.Entry(self.master, font=font)
        self.input1.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.master, text='Cognome:', font=font).grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.input2 = tk.Entry(self.master, font=font)
        self.input2.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.master, text='Età:', font=font).grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.input3 = tk.Entry(self.master, font=font)
        self.input3.grid(row=2, column=1, padx=10, pady=10)
        tk.Button(self.master, text='Salva', font=font, command=self.salva_dati).grid(row=3, column=0, columnspan=2, pady=10)
        
        # casella di testo
        self.textbox = tk.Text(self.master, font=font, state='disabled')
        self.textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        ttk.Separator(self.master, orient='horizontal').grid(row=5, column=0, columnspan=2, pady=10, sticky='ew')

        # pulsante 
        tk.Button(self.master, text='Aggiorna dati', font=font, command=self.update_data).grid(row=6, column=0, columnspan=2, pady=10)
        
        self.input3.bind('<Return>', lambda event: self.salva_dati()) #invio
        self.input1.focus_set()#focus inizio
        self.input1.icursor(tk.END)#cursor


        # Creo casella di testo in sola lettura
        self.textbox = tk.Text(self.master, font=font, wrap='none', state='disabled')
        self.textbox.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        # Scrivo
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