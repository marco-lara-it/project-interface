import tkinter as tk
import tkinter.ttk as ttk
import os
import pickle
import gspread
from tkinter import messagebox
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from tkcalendar import DateEntry
from datetime import date
import datetime
from tkcalendar import DateEntry
from PIL import Image, ImageTk
from googleapiclient.errors import HttpError
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Costanti e configurazione
SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
SAMPLE_SPREADSHEET_ID_input = '1ssWRMfTWKkjD-JdC2Vp2r6b9NlMsh7omqNq_bRW-kdw'
SAMPLE_RANGE_NAME = 'A1:AA1000'
creds = None

class GoogleSheetAuth:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    SAMPLE_SPREADSHEET_ID_input = '1ssWRMfTWKkjD-JdC2Vp2r6b9NlMsh7omqNq_bRW-kdw'
    SAMPLE_RANGE_NAME = 'A1:AA1000'
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                self.creds = pickle.load(token)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('token.pickle', 'wb') as token:
                pickle.dump(self.creds, token)

    def get_credentials(self):
        return gspread.authorize(self.creds)
    
class MyApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title('MANAGING APP')

        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        screen_width = int(screen_width * 2 / 3)
        self.master.geometry(f"{screen_width}x{screen_height}")
        self.master.resizable(True, True)
        self.initUI()
        self.pack()

    def initUI(self):
        self.style = ttk.Style()
        self.style.theme_use('default')
        self.style.configure('TLabel', font=('TkDefaultFont', 20), padding=10)
        self.style.configure('TEntry', font=('TkDefaultFont', 20), padding=10)
        self.style.configure('TButton', font=('TkDefaultFont', 20), padding=10)

        container = tk.Frame(self.master)
        container.pack(fill='both', expand=True)

        self.frames = {}

        for F in (LoginPage, HomePage, Spese, Clienti, Indicatori):
            frame = F(container, self)
            self.frames[F] = frame

        for frame in self.frames.values():
            frame.pack_forget()
        self.frames[LoginPage].pack(fill='both', expand=True)
        container.pack(fill='both', expand=True)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        for f in self.frames.values():
            f.pack_forget()
        frame.pack(fill='both', expand=True)


class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.pack(expand=True)

        self.login_frame = ttk.Frame(self)
        self.login_frame.pack(expand=True)

        self.instructions_label = ttk.Label(self.login_frame, text="Inserisci l'username e la password per accedere all'app:")
        self.instructions_label.pack(pady=10)

        self.username_label = ttk.Label(self.login_frame, text="Username")
        self.username_label.pack(side="top", padx=10, pady=10)
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.pack(side="top", padx=10, pady=10)

        self.password_label = ttk.Label(self.login_frame, text="Password")
        self.password_label.pack(side="top", padx=10, pady=10)
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.pack(side="top", padx=10, pady=10)

        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbutton = ttk.Checkbutton(self.login_frame, text="Mostra password", variable=self.show_password_var, command=lambda: self.mostra_password(self.password_entry))
        self.show_password_checkbutton.pack(side="top", padx=10, pady=10)

        self.login_button = ttk.Button(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(side="top", padx=10, pady=10)

        self.add_credentials_button = ttk.Button(self.login_frame, text="Registrati", command=self.create_credentials)
        self.add_credentials_button.pack(side="top", padx=10, pady=10)

        self.username_entry.bind("<Return>", lambda event: self.password_entry.focus())
        self.password_entry.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        try:
            gc = GoogleSheetAuth.get_instance().get_credentials()
            sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input)
            worksheet = sheet.worksheet("Foglio3")
            values = worksheet.get_all_values()

            for row in values:
                if len(row) >= 2 and row[0] == username and row[1] == password:
                    self.controller.show_frame(HomePage)
                    return
                
            tk.messagebox.showerror("Errore", "Username o password non corretti")

        except HttpError as error:
            print(f"Si è verificato un errore: {error}")
            tk.messagebox.showerror("Errore", "Impossibile accedere al foglio di Google Sheets")

    def create_credentials(self):

        new_credentials_window = tk.Toplevel(self.master)
        new_credentials_window.title("Crea nuove credenziali")

        new_credentials_frame = ttk.Frame(new_credentials_window)
        new_credentials_frame.pack(expand=True)

        new_username_label = ttk.Label(new_credentials_frame, text="Nuovo Username:")
        new_username_label.pack(side="top", padx=10, pady=10)
        self.new_username_entry = ttk.Entry(new_credentials_frame)
        self.new_username_entry.pack(side="top", padx=10, pady=10)

        new_password_label = ttk.Label(new_credentials_frame, text="Nuova Password:")
        new_password_label.pack(side="top", padx=10, pady=10)
        self.new_password_entry = ttk.Entry(new_credentials_frame, show="*")
        self.new_password_entry.pack(side="top", padx=10, pady=10)

        new_password_confirm_label = ttk.Label(new_credentials_frame, text="Conferma Password:")
        new_password_confirm_label.pack(side="top", padx=10, pady=10)
        self.new_password_confirm_entry = ttk.Entry(new_credentials_frame, show="*")
        self.new_password_confirm_entry.pack(side="top", padx=10, pady=10)

        self.show_new_password_var = tk.BooleanVar()
        self.show_new_password_checkbutton = ttk.Checkbutton(new_credentials_frame, text="Mostra password", variable=self.show_new_password_var, command=lambda: self.mostra_password(self.new_password_entry, self.new_password_confirm_entry))
        self.show_new_password_checkbutton.pack(side="top", padx=10, pady=10)

        add_credentials_button = ttk.Button(new_credentials_frame, text="Aggiungi", command=lambda: self.add_credentials(new_credentials_window))
        add_credentials_button.pack(side="top", padx=10, pady=10)

    def add_credentials(self, new_credentials_window):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()
        new_password_confirm = self.new_password_confirm_entry.get()

        if new_password != new_password_confirm:
            tk.messagebox.showerror("Errore", "Le due password non corrispondono")
            return

        try:
            gc = GoogleSheetAuth.get_instance().get_credentials()
            sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input)
            worksheet = sheet.worksheet("Foglio3")
            values = worksheet.get_all_values()

            for row in values:
                if row[0] == new_username:
                    tk.messagebox.showerror("Errore", "Username già esistente")
                    return

            new_range = f"A{len(values) + 1}:B{len(values) + 1}"
            result = worksheet.update(new_range, [[new_username, new_password]], value_input_option="USER_ENTERED")

            new_credentials_window.destroy()

        except HttpError as error:
            print(f"Si è verificato un errore: {error}")
            tk.messagebox.showerror("Errore", "Impossibile aggiungere nuove credenziali al foglio di Google Sheets")
            
    def mostra_password(self, *entries):
        for entry in entries:
            if entry.cget('show') == "":
                entry.config(show="*")
            else:
                entry.config(show="")

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = ttk.Label(self, text='Home Page', font=('TkDefaultFont', 20))
        label.grid(row=0, column=0, columnspan=3, pady=20)
        description_label = tk.Label(self, text='Benvenuto nell\'applicazione.\n'
                                                'Questa è la Home Page, da qui puoi accedere alle diverse funzionalità.',
                                      font=('TkDefaultFont', 26), justify='center')
        description_label.grid(row=1, column=0, columnspan=3, pady=20)
        bilancio_icon = Image.open("bilancio_icon.png")
        bilancio_icon = bilancio_icon.resize((64, 64), Image.LANCZOS)
        bilancio_icon = ImageTk.PhotoImage(bilancio_icon)
        button1 = ttk.Button(self, text="Spese", image=bilancio_icon, compound=tk.TOP, command=lambda: controller.show_frame(Spese))
        button1.image = bilancio_icon  
        button1.grid(row=2, column=0, padx=20, pady=10)
        clienti_icon = Image.open("clienti_icon.png")
        clienti_icon = clienti_icon.resize((64, 64), Image.LANCZOS)
        clienti_icon = ImageTk.PhotoImage(clienti_icon)
        button2 = ttk.Button(self, text="Clienti", image=clienti_icon, compound=tk.TOP, command=lambda: controller.show_frame(Clienti))
        button2.image = clienti_icon  
        button2.grid(row=2, column=1, padx=20, pady=10)
        indicatori_icon = Image.open("indicatori_icon.png")
        indicatori_icon = indicatori_icon.resize((64, 64), Image.LANCZOS)
        indicatori_icon = ImageTk.PhotoImage(indicatori_icon)
        button3 = ttk.Button(self, text="Indicatori", image=indicatori_icon, compound=tk.TOP, command=lambda: controller.show_frame(Indicatori))
        button3.image = indicatori_icon
        button3.grid(row=2, column=2, padx=20, pady=10)
        home_icon = Image.open("home_icon.png")
        home_icon = home_icon.resize((32, 32), Image.LANCZOS)
        home_icon = ImageTk.PhotoImage(home_icon)
        button4 = ttk.Button(self, text="Home", image=home_icon, compound=tk.TOP, command=lambda: controller.show_frame(HomePage))
        button4.image = home_icon
        button4.grid(row=3, column=1, padx=20, pady=10)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=3)
        self.rowconfigure(3, weight=1)

class Spese(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.setup_frames()
        self.setup_header()
        self.setup_causale()
        self.setup_importo()
        self.setup_data()
        self.setup_indicator()
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
        self.indicator_frame = tk.Frame(self)
        self.indicator_frame.pack(side="top", anchor="e", padx=10, pady=10)
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, padx=10, pady=10, expand=True)

    def setup_header(self):
        label = ttk.Label(self.header_frame, text='Spese', font=('DefaultFont', 20))
        label.pack(side=tk.LEFT, padx=10, pady=10)
        button = ttk.Button(self.header_frame, text='Torna alla Homepage', command=lambda: self.controller.show_frame(HomePage))
        button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def setup_indicator(self):
        font = ('TkDefaultFont', 16)

        ttk.Label(self.indicator_frame, text='Somma degli importi:', font=font).pack(side="left", padx=10)
        self.somma_importi_label = ttk.Label(self.indicator_frame, text='', font=font)
        self.somma_importi_label.pack(side="left", padx=10)
        self.update_somma_importi()

    def update_somma_importi(self):
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input).sheet1
        data = sheet.get_all_values()
        somma_importi = sum(float(row[1]) for row in data if row[1])
        self.somma_importi_label.config(text='€ {:.2f}'.format(somma_importi))

        
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
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input).sheet1
        data = sheet.get_all_values()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in data:
            self.tree.insert('', 'end', values=row)

        self.update_somma_importi()


    def salva_dati(self):
        causale = self.causale_var.get().strip()
        importo = self.input2.get().strip()
        data_selezionata = self.input3.get_date()
        data_string = data_selezionata.strftime('%Y-%m-%d')

        if causale and importo and data_string:
            data_to_write = [[causale, importo, data_string]]
            body = {'values': data_to_write}

            gc = GoogleSheetAuth.get_instance().get_credentials()
            sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input).sheet1

            result = sheet.append_rows(data_to_write, value_input_option='RAW')

            if len(data_to_write) > 0:
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
        columns = ('Cliente', 'Pezzi venduti', 'Data vendita', 'Data uscita')

        tree_frame = ttk.Frame(self)  # Create a frame to contain the treeview and scrollbar
        tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)  # Set the height of the treeview
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Data uscita":
                self.tree.column(col, stretch=True, width=100)
            elif col != "Data vendita":
                self.tree.column(col, stretch=True, width=200)
            else:
                self.tree.column(col, stretch=True, width=100)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

    def setup_buttons(self):
        button1 = ttk.Button(self, text='Aggiorna dati', command=self.update_data)
        button1.pack(padx=10, pady=10)

        button2 = ttk.Button(self, text='Torna alla Homepage', command=lambda: self.controller.show_frame(HomePage))
        button2.pack(padx=10, pady=10)

    def update_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        gc = GoogleSheetAuth.get_instance().get_credentials()  # Utilizza la classe GoogleSheetAuth per ottenere le credenziali
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1)  # 1 indica il secondo foglio (Foglio2)
        data = sheet2.get_all_values()
        
        for row in data:
            if len(row) >= 4:  # Cambia il valore da 3 a 4
                self.tree.insert('', 'end', values=(row[0], row[1], row[2], row[3]))  
            else:
                self.tree.insert('', 'end', values=(row[0], row[1], '', ''))

class Indicatori(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.expenses_data = []
        self.update_expenses_data()
        self.clients_data = []
        self.update_clients_data()

        label = ttk.Label(self, text='Indicatori', font=('TkDefaultFont', 30))
        label.pack(pady=50)

        description_label = tk.Label(self, text='Questa pagina mostra alcuni indicatori.', font=('TkDefaultFont', 20))
        description_label.pack(pady=10)

        sum_frame = tk.Frame(self)
        sum_frame.pack(pady=10)
        somma_col2 = self.get_sum_of_column_2()
        tk.Label(sum_frame, text='1) Somma delle spese registrate:', font=('TkDefaultFont', 24)).pack(side=tk.LEFT)
        self.somma_col2_label = tk.Label(sum_frame, text='€ {:.2f}'.format(somma_col2), font=('TkDefaultFont', 24))
        self.somma_col2_label.pack(side=tk.LEFT)

        pie_chart_caption = tk.Label(self, text='2) Grafico clienti e pezzi', font=('TkDefaultFont', 24))
        pie_chart_caption.pack(pady=10)

        pie_chart_button = ttk.Button(self, text='Mostra grafico', command=self.show_pie_chart)
        pie_chart_button.pack(pady=20)

        turnover_frame = tk.Frame(self)
        turnover_frame.pack(pady=10)
        self.avarage_days = 0
        self.update_clients_data()
        grouped_data, self.avarage_days = self.day_indicator()
        tk.Label(turnover_frame, text='3) Tempo medio di giacenza del magazzino:', font=('TkDefaultFont', 24)).pack(side=tk.LEFT)
        self.avarage_days_label = tk.Label(turnover_frame, text='{:.2f} giorni'.format(self.avarage_days), font=('TkDefaultFont', 24))
        self.avarage_days_label.pack(side=tk.LEFT)

        update_button = ttk.Button(self, text='Aggiorna Indicatori', command=self.update_indicators)
        update_button.pack(pady=20)

        back_button = ttk.Button(self, text='Torna alla Homepage', command=lambda: controller.show_frame(HomePage))
        back_button.pack(pady=50)


    def update_expenses_data(self):
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet1 = sheet.get_worksheet(0)
        self.expenses_data = sheet1.get_all_values()

    def get_sum_of_column_2(self):
        col_values = [row[1] for row in self.expenses_data]
        return sum(float(val) for val in col_values if val)
    
    def update_clients_data(self):
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1)  # 1 indica il secondo foglio (Foglio2)
        self.clients_data = sheet2.get_all_values()

    def update_indicators(self):
        self.update_expenses_data()
        self.update_clients_data()
        somma_col2 = self.get_sum_of_column_2()
        self.somma_col2_label.config(text='€ {:.2f}'.format(somma_col2))
        grouped_data, self.avarage_days = self.day_indicator()
        self.avarage_days_label.config(text='{:.2f} giorni'.format(self.avarage_days))

    def show_pie_chart(self):
        self.update_clients_data()
        grouped_data, _ = self.day_indicator()  
        labels = list(grouped_data.keys())
        sizes = list(grouped_data.values())

        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Distribuzione pezzi venduti per cliente')
        plt.show()

    
    def get_data(self):
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1)  # 1 indica il secondo foglio (Foglio2)
        return sheet2.get_all_values()
    
    def day_indicator(self):
        grouped_data = {}
        total_days = 0
        total_orders = 0
        for row in self.clients_data:
            client = row[0]
            pezzi_venduti = int(row[1])
            entry_date = datetime.datetime.strptime(row[2], "%d/%m/%Y")
            exit_date = datetime.datetime.strptime(row[3], "%d/%m/%Y")
            days_difference = (exit_date - entry_date).days
            if days_difference < 0:
                days_difference = 0
                
            total_days += days_difference
            total_orders += 1
            if client in grouped_data:
                grouped_data[client] += pezzi_venduti
            else:
                grouped_data[client] = pezzi_venduti
        average_days = total_days / total_orders
        return grouped_data, average_days

if __name__ == '__main__':
    root = tk.Tk()
    ex = MyApp(root)
    root.mainloop()