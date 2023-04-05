import tkinter as tk
import tkinter.ttk as ttk
import os
import pickle
import gspread
from tkinter import messagebox
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from datetime import date
from tkcalendar import DateEntry

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

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        screen_width = int(screen_width * 2 / 3)
        self.master.geometry(f"{screen_width}x{screen_height}")
        self.master.resizable(True, True)
        self.initUI()

    def initUI(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TLabel', font=('TkDefaultFont', 20), padding=10)
        self.style.configure('TEntry', font=('TkDefaultFont', 20), padding=10)
        self.style.configure('TButton', font=('TkDefaultFont', 20), padding=10)

        container = tk.Frame(self.master)
        container.pack(fill='both', expand=True)

        self.frames = {}

        for F in (HomePage, Bilancio, PageTwo):
            frame = F(container, self)
            self.frames[F] = frame
            frame.pack(fill='both', expand=True)

        self.show_frame(HomePage)

    def show_frame(self, cont):
        for frame in self.frames.values():
            frame.pack_forget()
        frame = self.frames[cont]
        frame.pack(fill='both', expand=True)


class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self,text='Home Page', font=('TkDefaultFont', 20))
        label.pack(padx=10, pady=10)
        description_label = tk.Label(self, text='Benvenuto nell\'applicazione di prova.\n'
                                            'Questa è la Home Page, da qui puoi accedere alle diverse funzionalità.\n'
                                            'Scegli una delle opzioni dal menu per iniziare!', 
                                            font=('TkDefaultFont', 18), justify='center')
        description_label.pack(padx=20, pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(side="top", fill="both", expand=True, padx=20)

        left_column = tk.Frame(button_frame)
        left_column.pack(side="left", fill="both", expand=True)
        button1 = ttk.Button(left_column, text="Bilancio", command=lambda: controller.show_frame(Bilancio))
        button1.pack(side="top", pady=10)

        right_column = tk.Frame(button_frame)
        right_column.pack(side="left", fill="both", expand=True)
        button2 = ttk.Button(right_column, text="Pagina 2", command=lambda: controller.show_frame(PageTwo))
        button2.pack(side="top", pady=10)


class Bilancio(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        def validate_numeric_input(new_value):
            if new_value == "":
                return True
            try:
                float(new_value)
                return True
            except ValueError:
                return False

        # Crea un frame per contenere la label e il pulsante
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)

        # Label 'Bilancio'
        label = ttk.Label(header_frame, text='Bilancio', font=('DefaultFont', 20))
        label.pack(side=tk.LEFT, padx=10, pady=10)
        # Pulsante 'Go back to Home Page'
        button = ttk.Button(header_frame, text='Go back to Home Page', command=lambda: controller.show_frame(HomePage))
        button.pack(side=tk.RIGHT, padx=10, pady=10)

        font = ('TkDefaultFont', 18)
        input_width = 20

        #causale
        causale_frame = tk.Frame(self)
        causale_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(causale_frame, text='Causale:', font=font, anchor='w').pack(side=tk.LEFT, padx=10)
        causale_var = tk.StringVar(self)
        causale_var.set("Seleziona causale") 
        opzioni_causale = ["Magazzino", "Personale", "Gestione"] 
        self.input1 = ttk.Combobox(causale_frame, font=font, textvariable=causale_var, values=opzioni_causale, state='readonly', width=input_width)
        self.input1.pack(side=tk.LEFT, padx=10)
        self.input1.bind("<FocusIn>", lambda event: self.input1.configure(values=opzioni_causale))

        # Importo
        importo_frame = tk.Frame(self)
        importo_frame.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(importo_frame, text='Importo:', font=font, anchor='w').pack(side=tk.LEFT, padx=10)
        vcmd = (self.register(validate_numeric_input), '%P')
        style = ttk.Style()
        style.configure('Custom.TEntry', height=1)
        self.input2 = ttk.Entry(importo_frame, font=font, width=20, validate="key", validatecommand=vcmd, style='Custom.TEntry')
        self.input2.pack(side=tk.LEFT, padx=10)

        # Data
        data_frame = tk.Frame(self)
        data_frame.pack(fill=tk.X, padx=10, pady=10)
        today = date.today()
        tk.Label(data_frame, text='Data:', font=font, anchor='w').pack(side=tk.LEFT, padx=10)
        self.input3 = DateEntry(data_frame, font=font, date_pattern='yyyy-mm-dd')
        self.input3.set_date(today)
        self.input3.config(state='abled')
        self.input3.pack(side=tk.LEFT, padx=10)

        # Salva
        tk.Button(self, text='Salva', font=font, command=self.salva_dati, width=15, bg='white').pack(fill=tk.X, padx=10, pady=10)
        text_frame = tk.Frame(self)
        text_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

        # text box
        self.textbox = tk.Text(text_frame, font=('TkDefaultFont', 18), state='disabled', wrap='none', height=10, spacing1=5, spacing2=50)
        self.textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # scroll bar
        scrollbar = tk.Scrollbar(text_frame, command=self.textbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.textbox.configure(yscrollcommand=scrollbar.set)
        ttk.Separator(self, orient='horizontal').pack(fill=tk.X, padx=10, pady=10)

        # pulsante 
        tk.Button(self, text='Aggiorna dati', font=font, command=self.update_data, width=15, bg='white').pack(fill=tk.X, padx=10, pady=10)

        # eventi
        self.input3.bind('<Return>', lambda event: self.salva_dati())  # invio
        self.input1.focus_set()  # focus inizio
        self.input1.icursor(tk.END)  # cursor

        # tema
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TLabel', font=font, padding=10)
        style.configure('TEntry', font=font, padding=10)
        style.configure('TButton', font=font, padding=10)
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
        causale = self.input1.get().strip()
        importo = self.input2.get().strip()
        data_selezionata = self.input3.get_date()
        data_string = data_selezionata.strftime('%Y-%m-%d')
        
        if causale and importo and data_string:
            data_to_write = [[causale, importo, data_string]]
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


class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        label = ttk.Label(self, text='Page Two', font=('TkDefaultFont', 20))
        label.pack(padx=10, pady=10)
        button = ttk.Button(self, text='Go back to Home Page', command=lambda: controller.show_frame(HomePage))
        button.pack(padx=10, pady=10)

if __name__ == '__main__':
    root = tk.Tk()
    ex = MyApp(root)
    root.mainloop() 