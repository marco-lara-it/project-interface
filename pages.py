import tkinter as tk
import tkinter.ttk as ttk
import os
import pickle
import gspread
from tkinter import messagebox
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
import calendar
from datetime import date
from tkcalendar import DateEntry
from PIL import Image, ImageTk

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

        for F in (HomePage, Bilancio, Clienti):
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

        # Header
        label = ttk.Label(self, text='Home Page', font=('TkDefaultFont', 20))
        label.grid(row=0, column=0, columnspan=2, pady=20)

        # Description
        description_label = tk.Label(self, text='Benvenuto nell\'applicazione di prova.\n'
                                                'Questa è la Home Page, da qui puoi accedere alle diverse funzionalità.\n'
                                                'Scegli una delle opzioni dal menu per iniziare!',
                                      font=('TkDefaultFont', 28), justify='center')
        description_label.grid(row=1, column=0, columnspan=2, pady=20)

        # Bilancio button
        bilancio_icon = Image.open("bilancio_icon.png")
        bilancio_icon = bilancio_icon.resize((64, 64), Image.LANCZOS)
        bilancio_icon = ImageTk.PhotoImage(bilancio_icon)
        button1 = ttk.Button(self, text="Bilancio", image=bilancio_icon, compound=tk.TOP, command=lambda: controller.show_frame(Bilancio))
        button1.image = bilancio_icon  
        button1.grid(row=2, column=0, padx=20, pady=10)

        # Clienti button
        clienti_icon = Image.open("clienti_icon.png")
        clienti_icon = clienti_icon.resize((64, 64), Image.LANCZOS)
        clienti_icon = ImageTk.PhotoImage(clienti_icon)
        button2 = ttk.Button(self, text="Clienti", image=clienti_icon, compound=tk.TOP, command=lambda: controller.show_frame(Clienti))
        button2.image = clienti_icon  
        button2.grid(row=2, column=1, padx=20, pady=10)

        # Grid configuration
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=3)

class Bilancio(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.setup_frames()
        self.setup_header()
        self.setup_causale()
        self.setup_importo()
        self.setup_data()
        self.setup_salva_button()
        self.setup_treeview()
        self.setup_aggiorna_button()
        self.update_data()

    def setup_frames(self):
        self.header_frame = tk.Frame(self)
        self.header_frame.pack(fill=tk.X, padx=10, pady=10)

        self.causale_frame = tk.Frame(self)
        self.causale_frame.pack(side="top", anchor="w", padx=10, pady=10)

        self.importo_frame = tk.Frame(self)
        self.importo_frame.pack(side="top", anchor="w", padx=10, pady=10)

        self.data_frame = tk.Frame(self)
        self.data_frame.pack(side="top", anchor="w", padx=10, pady=10)

        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

    def setup_header(self):
        label = ttk.Label(self.header_frame, text='Bilancio', font=('DefaultFont', 20))
        label.pack(side=tk.LEFT, padx=10, pady=10)
        button = ttk.Button(self.header_frame, text='Go back to Home Page', command=lambda: self.controller.show_frame(HomePage))
        button.pack(side=tk.RIGHT, padx=10, pady=10)

    def setup_causale(self):
        font = ('TkDefaultFont', 16)
        input_width = 25

        ttk.Label(self.causale_frame, text='Causale:', font=font).pack(side="left", padx=10)
        self.causale_options = ['Personale', 'Fornitori', 'Gestionale']
        self.causale_var = tk.StringVar()
        self.input1 = ttk.Combobox(self.causale_frame, textvariable=self.causale_var, values=self.causale_options, state='readonly', width=input_width)
        self.input1.set(self.causale_options[0])  # Set the default option
        self.input1.pack(side="left", padx=10)
        self.input1.bind('<Return>', lambda event: self.salva_dati())



    def setup_importo(self):
        font = ('TkDefaultFont', 16)
        input_width = 25

        def validate_numeric_input(new_value):
            if new_value == "":
                return True
            try:
                float(new_value)
                return True
            except ValueError:
                return False

        vcmd = (self.register(validate_numeric_input), "%P")
        ttk.Label(self.importo_frame, text='Importo:', font=font).pack(side="left", padx=10)
        self.input2 = ttk.Entry(self.importo_frame, validate="key", validatecommand=vcmd, width=input_width)
        self.input2.pack(side="left", padx=10)
        self.input2.bind('<Return>', lambda event: self.salva_dati())


    def setup_data(self):
        font = ('TkDefaultFont', 16)
        input_width = 25
        ttk.Label(self.data_frame, text='Data:', font=font).pack(side="left", padx=10)
        self.input3 = DateEntry(self.data_frame, date_pattern='dd.mm.yyyy', background='darkblue', foreground='white', borderwidth=2, width=input_width)
        self.input3.pack(side="left", padx=10)
        self.input3.bind('<Return>', lambda event: self.salva_dati())

    def setup_salva_button(self):
        font = ('TkDefaultFont', 16)
        tk.Button(self, text='Salva', font=font, command=self.salva_dati, width=15, bg='white').pack(fill=tk.X, padx=10, pady=10)

    def setup_treeview(self):
        columns = ('Causale', 'Importo', 'Data')
        
        self.tree = ttk.Treeview(self.text_frame, columns=columns, show='headings', height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, stretch=True, width=150)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

    def setup_aggiorna_button(self):
        font = ('TkDefaultFont', 16)
        tk.Button(self, text='Aggiorna dati', font=font, command=self.update_data, width=15, bg='white').pack(fill=tk.X, padx=10, pady=10)

    def update_data(self):
            gs = gspread.authorize(creds)
            sheet = gs.open_by_key(SAMPLE_SPREADSHEET_ID_input).sheet1
            data = sheet.get_all_values()

            for i in self.tree.get_children():
                self.tree.delete(i)

            for row in data:
                self.tree.insert('', 'end', values=row)


    def salva_dati(self):
        causale = self.causale_var.get().strip()
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


class Clienti(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.setup_header()
        self.setup_treeview()
        self.setup_buttons()
        self.update_data()

    def setup_header(self):
        label = ttk.Label(self, text='Clienti', font=('TkDefaultFont', 20))
        label.pack(padx=10, pady=10)

    def setup_treeview(self):
        columns = ('Cliente', 'Pezzi venduti')
        
        tree_frame = ttk.Frame(self)  # Create a frame to contain the treeview and scrollbar
        tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)  # Set the height of the treeview
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, stretch=True, width=200)  # Set the width of the columns
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

    def setup_buttons(self):
        button1 = ttk.Button(self, text='Aggiorna dati', command=self.update_data)
        button1.pack(padx=10, pady=10)

        button2 = ttk.Button(self, text='Go back to Home Page', command=lambda: self.controller.show_frame(HomePage))
        button2.pack(padx=10, pady=10)
    
    def update_data(self):
        # Clear the treeview
        for i in self.tree.get_children():
            self.tree.delete(i)


        # Google Sheet
        gs = gspread.authorize(creds)
        sheet = gs.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1)  # 1 indica il secondo foglio (Foglio2), poiché gli indici partono da 0
        data = sheet2.get_all_values()
        for row in data:
            self.tree.insert('', 'end', values=(row[0], row[1]))

if __name__ == '__main__':
    root = tk.Tk()
    ex = MyApp(root)
    root.mainloop()