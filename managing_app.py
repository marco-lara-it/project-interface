import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
from PIL import Image
from PIL import ImageTk
from customtkinter.windows.widgets.image.ctk_image import CTkImage
import os
import pickle
import gspread
from tkinter import messagebox
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from google.auth.transport.requests import Request
from tkcalendar import DateEntry
from datetime import datetime, date
from tkcalendar import DateEntry
from googleapiclient.errors import HttpError
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import statistics
from scipy.stats import norm
import math
import numpy as np

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
        container = tk.Frame(self.master)
        container.pack(fill='both', expand=True)

        self.frames = {}

        # Configura lo stile per i widget di customtkinter
        ctk.CTkLabel.default_font = ('TkDefaultFont', 20)
        ctk.CTkEntry.default_font = ('TkDefaultFont', 20)
        ctk.CTkButton.default_font = ('TkDefaultFont', 20)

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

        self.login_frame = ctk.CTkFrame(self)
        self.login_frame.pack(expand=True)

        self.instructions_label = ctk.CTkLabel(self.login_frame, text="Inserisci l'username e la password per accedere all'app:")
        self.instructions_label.pack(pady=10)

        self.username_label = ctk.CTkLabel(self.login_frame, text="Username")
        self.username_label.pack(side="top", padx=10, pady=10)
        self.username_entry = ctk.CTkEntry(self.login_frame)
        self.username_entry.pack(side="top", padx=10, pady=10)

        self.password_label = ctk.CTkLabel(self.login_frame, text="Password")
        self.password_label.pack(side="top", padx=10, pady=10)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.password_entry.pack(side="top", padx=10, pady=10)

        self.show_password_var = tk.BooleanVar()
        self.show_password_checkbutton = ctk.CTkCheckBox(self.login_frame, text="Mostra password", variable=self.show_password_var, command=lambda: self.mostra_password(self.password_entry))
        self.show_password_checkbutton.pack(side="top", padx=10, pady=10)

        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(side="top", padx=10, pady=10)

        self.add_credentials_button = ctk.CTkButton(self.login_frame, text="Registrati", command=self.create_credentials)
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

        new_credentials_frame = ctk.CTkFrame(new_credentials_window)
        new_credentials_frame.pack(expand=True)

        new_username_label = ctk.CTkLabel(new_credentials_frame, text="Nuovo Username:")
        new_username_label.pack(side="top", padx=10, pady=10)
        self.new_username_entry = ctk.CTkEntry(new_credentials_frame)
        self.new_username_entry.pack(side="top", padx=10, pady=10)

        new_password_label = ctk.CTkLabel(new_credentials_frame, text="Nuova Password:")
        new_password_label.pack(side="top", padx=10, pady=10)
        self.new_password_entry = ctk.CTkEntry(new_credentials_frame, show="*")
        self.new_password_entry.pack(side="top", padx=10, pady=10)

        new_password_confirm_label = ctk.CTkLabel(new_credentials_frame, text="Conferma Password:")
        new_password_confirm_label.pack(side="top", padx=10, pady=10)
        self.new_password_confirm_entry = ctk.CTkEntry(new_credentials_frame, show="*")
        self.new_password_confirm_entry.pack(side="top", padx=10, pady=10)

        self.role_label = ctk.CTkLabel(new_credentials_frame, text="Ruolo:")
        self.role_label.pack(side="top", padx=10, pady=10)
        self.role_combobox = ctk.CTkComboBox(new_credentials_frame, values=[ "vendite", "contabile","analista"], state="readonly")
        self.role_combobox.set("vendite")  # Imposta il valore predefinito su 'vendite'
        self.role_combobox.pack(side="top", padx=10, pady=10)

        self.show_new_password_var = tk.BooleanVar()
        self.show_new_password_checkbutton = ctk.CTkCheckBox(new_credentials_frame, text="Mostra password", variable=self.show_new_password_var, command=lambda: self.mostra_password(self.new_password_entry, self.new_password_confirm_entry))
        self.show_new_password_checkbutton.pack(side="top", padx=10, pady=10)

        add_credentials_button = ctk.CTkButton(new_credentials_frame, text="Aggiungi", command=lambda: self.add_credentials(new_credentials_window))
        add_credentials_button.pack(side="top", padx=10, pady=10)

    def add_credentials(self, new_credentials_window):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()
        new_password_confirm = self.new_password_confirm_entry.get()
        new_role = self.role_combobox.get()
        
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

            new_range = f"A{len(values) + 1}:C{len(values) + 1}"
            result = worksheet.update(new_range, [[new_username, new_password, new_role]], value_input_option="USER_ENTERED")

            new_credentials_window.destroy()

        except HttpError as error:
            print(f"Si è verificato un errore: {error}")
            tk.messagebox.showerror("Errore", "Impossibile aggiungere nuove credenziali al foglio di Google Sheets")
            
    def mostra_password(self, *entries):
        for entry in entries:
            if entry.cget('show') == "":
                entry.configure(show="*")
            else:
                entry.configure(show="")

class HomePage(ctk.CTkFrame):
    def __init__(self, parent, controller):
        ctk.CTkFrame.__init__(self, parent)
        self.controller = controller
        label = ctk.CTkLabel(self, text='Home Page', font=('TkDefaultFont', 20))
        label.grid(row=0, column=0, columnspan=3, pady=20)

        description_label = ctk.CTkLabel(self, text='Benvenuto nell\'applicazione.\nQuesta è la Home Page, da qui puoi accedere alle diverse funzionalità.', font=('TkDefaultFont', 26), justify='center')
        description_label.grid(row=1, column=0, columnspan=3, pady=20)

        bilancio_icon = Image.open("bilancio_icon.png")
        bilancio_icon = bilancio_icon.resize((64, 64), Image.LANCZOS)
        bilancio_icon = ImageTk.PhotoImage(bilancio_icon)
        button1 = ctk.CTkButton(self, text="Spese", image=bilancio_icon, compound=tk.TOP, command=lambda: self.check_permission(Spese, "contabile"))
        button1.image = bilancio_icon  
        button1.grid(row=2, column=0, padx=20, pady=10)

        clienti_icon = Image.open("clienti_icon.png")
        clienti_icon = clienti_icon.resize((64, 64), Image.LANCZOS)
        clienti_icon = ImageTk.PhotoImage(clienti_icon)
        button2 = ctk.CTkButton(self, text="Clienti", image=clienti_icon, compound=tk.TOP, command=lambda: self.check_permission(Clienti, "vendite"))
        button2.image = clienti_icon  
        button2.grid(row=2, column=1, padx=20, pady=10)

        indicatori_icon = Image.open("indicatori_icon.png")
        indicatori_icon = indicatori_icon.resize((64, 64), Image.LANCZOS)
        indicatori_icon = ImageTk.PhotoImage(indicatori_icon)
        button3 = ctk.CTkButton(self, text="Indicatori", image=indicatori_icon, compound=tk.TOP, command=lambda: self.check_permission(Indicatori, "vendite"))
        button3.image = indicatori_icon
        button3.grid(row=2, column=2, padx=20, pady=10)

        home_icon = Image.open("home_icon.png")
        home_icon = home_icon.resize((32, 32), Image.LANCZOS)
        home_icon = ImageTk.PhotoImage(home_icon)
        button4 = ctk.CTkButton(self, text="HomePage", image=home_icon, compound=tk.TOP, command=lambda: controller.show_frame(HomePage))
        button4.image = home_icon
        button4.grid(row=3, column=1, padx=20, pady=10)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=3)

    def check_permission(self, target_frame, required_role):
        username = self.controller.frames[LoginPage].username_entry.get()
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input)
        worksheet = sheet.worksheet("Foglio3")
        values = worksheet.get_all_values()

        for row in values:
            if len(row) >= 3 and row[0] == username:
                user_role = row[2]
                break
        else:
            messagebox.showerror("Errore", "Impossibile trovare il ruolo dell'utente")
            return

        if user_role == "analista" or user_role == required_role:
            self.controller.show_frame(target_frame)
        else:
            messagebox.showerror("Errore", f"L'utente non ha il permesso di accedere a questa pagina (ruolo {required_role} richiesto)")

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
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill=ctk.X, padx=10, pady=10)
        self.causale_frame = ctk.CTkFrame(self) 
        self.causale_frame.pack(side="top", anchor="w", padx=10, pady=10 )
        self.importo_frame = ctk.CTkFrame(self)
        self.importo_frame.pack(side="top", anchor="w", padx=10, pady=10)
        self.data_frame = ctk.CTkFrame(self)
        self.data_frame.pack(side="top", anchor="w", padx=10, pady=10)
        self.indicator_frame = ctk.CTkFrame(self)
        self.indicator_frame.pack(side="top", anchor="e", padx=10, pady=10)
        self.text_frame = ctk.CTkFrame(self)
        self.text_frame.pack(fill=ctk.BOTH, padx=10, pady=10, expand=True)

    def setup_header(self):
        label = ctk.CTkLabel(self.header_frame, text='Spese', font=('DefaultFont', 20))
        label.pack(side=tk.LEFT, padx=10, pady=10)
        button = ctk.CTkButton(self.header_frame, text='Torna alla Homepage', command=lambda: self.controller.show_frame(HomePage))
        button.pack(side=tk.RIGHT, padx=10, pady=10)
    
    def setup_indicator(self):
        font = ('TkDefaultFont', 16)

        ctk.CTkLabel(self.indicator_frame, text='Somma delle spese:', font=font).pack(side="left", padx=10)
        self.somma_importi_label = ctk.CTkLabel(self.indicator_frame, text='', font=font)
        self.somma_importi_label.pack(side="left", padx=10)
        self.update_somma_importi()

    def update_somma_importi(self):
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input).sheet1
        data = sheet.get_all_values()
        somma_importi = sum(float(row[1]) for row in data if row[1])
        self.somma_importi_label.configure(text='€ {:.2f}'.format(somma_importi))

    def setup_causale(self):
        font = ('TkDefaultFont', 16)
        input_width = 250
        ctk.CTkLabel(self.causale_frame, text='Causale:', font=font).pack(side="left", padx=10)
        self.causale_options = ['Personale', 'Fornitori', 'Gestionale']
        self.input1 = ctk.CTkComboBox(self.causale_frame, values=self.causale_options, state='readonly', width=input_width)
        self.input1.set(self.causale_options[0])  # Set the default option
        self.input1.pack(side="left", padx=10)
        self.input1.bind('<Return>', lambda event: self.salva_dati())

    def setup_importo(self):
        font = ('TkDefaultFont', 16)
        input_width = 250

        def validate_numeric_input(new_value):
            if new_value == "":
                return True
            try:
                float(new_value)
                return True
            except ValueError:
                return False

        vcmd = (self.register(validate_numeric_input), "%P")
        ctk.CTkLabel(self.importo_frame, text='Importo:', font=font).pack(side="left", padx=10)
        self.input2 = ctk.CTkEntry(self.importo_frame, validate="key", validatecommand=vcmd, width=input_width)
        self.input2.pack(side="left", padx=10)
        self.input2.bind('<Return>', lambda event: self.salva_dati())

    def setup_data(self):
        font = ('TkDefaultFont', 16)
        input_width = 25
        ctk.CTkLabel(self.data_frame, text='Data:', font=font).pack(side="left", padx=10)
        self.input3 = DateEntry(self.data_frame, date_pattern='dd.mm.yyyy', background='darkblue', foreground='white', borderwidth=2, width=input_width)
        self.input3.pack(side="left", padx=10)
        self.input3.bind('<Return>', lambda event: self.salva_dati())

    def setup_salva_button(self):
        font = ('TkDefaultFont', 16)
        ctk.CTkButton(self, text='Salva', font=font, command=self.salva_dati, width=15).pack(fill=ctk.X, padx=10, pady=10)

    def setup_treeview(self):
        columns = ('Causale', 'Importo', 'Data')

        style = ttk.Style()
        style.configure("Custom.Treeview", background="white", foreground="black")
        style.configure("Custom.Treeview.Heading", background="white", foreground="black")
        style.configure("Custom.Vertical.TScrollbar", background="white", troughcolor="white")

        self.tree = ttk.Treeview(self.text_frame, columns=columns, show='headings', height=10, style="Custom.Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, stretch=True, width=150)

        self.tree.tag_configure("pari", background="lightgray")
        self.tree.tag_configure("dispari", background="white")

        data_list = [
            ("Personale", 1000, "2023-05-11"),
            ("Fornitori", 2000, "2023-05-12"),
            ("Gestionale", 1500, "2023-05-13"),
        ]

        for i, row_data in enumerate(data_list):
            row_tag = "pari" if i % 2 == 0 else "dispari"
            self.tree.insert('', 'end', values=row_data, tags=row_tag)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        vsb = ttk.Scrollbar(self.text_frame, orient="vertical", command=self.tree.yview, style="Custom.Vertical.TScrollbar")
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

    def setup_aggiorna_button(self):
        font = ('TkDefaultFont', 16)
        ctk.CTkButton(self, text='Aggiorna dati', font=font, command=self.update_data, width=15).pack(fill=ctk.X, padx=10, pady=10)

    def update_data(self):
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(GoogleSheetAuth.SAMPLE_SPREADSHEET_ID_input).sheet1
        data = sheet.get_all_values()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for index, row in enumerate(data):
            row_tag = "pari" if index % 2 == 0 else "dispari"
            self.tree.insert('', 'end', values=row, tags=row_tag)

        self.update_somma_importi()

    def salva_dati(self):
        causale = self.input1.get().strip()
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
        label = ctk.CTkLabel(self, text='Clienti', font=('TkDefaultFont', 20))
        label.pack(padx=10, pady=10)

    def setup_treeview(self):
        columns = ('Cliente', 'Pezzi venduti', 'Data ordine', 'Data spedizione')

        tree_frame = ctk.CTkFrame(self)
        tree_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20, style="Custom.Treeview")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "Data spedizione":
                self.tree.column(col, stretch=True, width=100)
            elif col != "Data ordine":
                self.tree.column(col, stretch=True, width=200)
            else:
                self.tree.column(col, stretch=True, width=100)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        style = ttk.Style()
        style.configure("Custom.Treeview", background="lightgray", foreground="black")#scritte
        style.configure("Custom.Treeview.Heading", background="white", foreground="white")
        style.configure("Custom.Vertical.TScrollbar", background="white", troughcolor="white")

        self.tree.tag_configure("pari", background="lightgray")
        self.tree.tag_configure("dispari", background="white")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview, style="Custom.Vertical.TScrollbar")
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)



    def setup_buttons(self):
        button1 = ctk.CTkButton(self, text='Aggiorna dati', command=self.update_data)
        button1.pack(padx=10, pady=10)

        button2 = ctk.CTkButton(self, text='Torna alla Homepage', command=lambda: self.controller.show_frame(HomePage))
        button2.pack(padx=10, pady=10)


    def update_data(self):
        self.tree.delete(*self.tree.get_children())

        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1)
        data = sheet2.get_all_values()

        for index, row in enumerate(data):
            row_tag = "pari" if index % 2 == 0 else "dispari"
            values = (row[0], row[1], row[2], row[3]) if len(row) >= 4 else (row[0], row[1], '', '')
            self.tree.insert('', 'end', values=values, tags=row_tag)

class Indicatori(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.start_date = tk.StringVar()
        self.end_date = tk.StringVar()
        self.controller = controller
        self.expenses_data = []
        self.update_expenses_data()
        self.clients_data = []
        self.update_clients_data()
        
        main_frame = tk.Frame(self)
        main_frame.place(relx=0.5, rely=0.5, anchor="center")

        label = ctk.CTkLabel(main_frame, text='Indicatori', font=('TkDefaultFont', 30))
        label.grid(row=0, column=0, pady=50, padx=20, columnspan=2)

        date_frame = tk.Frame(main_frame)
        date_frame.grid(row=1, column=0, pady=10, padx=20, columnspan=2)
        

        date_start_label = tk.Label(date_frame, text="Data inizio periodo:", font=("TkDefaultFont", 14))
        date_start_label.grid(row=0, column=0, padx=10)
        self.date_start = DateEntry(date_frame, width=12, background='blue', foreground='white', font=('TkDefaultFont', 14))
        self.date_start.grid(row=0, column=1, padx=10)

        # Set the default date for date_start
        self.date_start.set_date("01/01/2022")
        date_start_label.bind("<Enter>", lambda event: messagebox.showinfo("Messaggio di aiuto",
                                                                            "Inserisci la data di inizio e fine periodo. Il presente comando modifica gli indicatori 2, 3 e 5. Premere poi 'Aggiorna Indicatori' per aggiornare "))

        date_end_label = tk.Label(date_frame, text="Data fine periodo:", font=("TkDefaultFont", 14))
        date_end_label.grid(row=0, column=2, padx=10)
        self.date_end = DateEntry(date_frame, width=12, background='blue', foreground='white', font=('TkDefaultFont', 14))
        self.date_end.grid(row=0, column=3, padx=10)

        description_label = ctk.CTkLabel(main_frame, text='Questa pagina mostra alcuni indicatori.', font=('TkDefaultFont', 20))
        description_label.grid(row=2, column=0, pady=10, padx=20, columnspan=2)

        sum_frame = tk.Frame(main_frame)
        sum_frame.grid(row=3, column=0, pady=10, padx=20, columnspan=2)
        somma_col2 = self.get_sum_of_column_2()
        tk.Label(sum_frame, text='1) Somma delle spese registrate (2023):', font=('TkDefaultFont', 24)).grid(row=0, column=0, padx=10)
        self.somma_col2_label = tk.Label(sum_frame, text='€ {:.2f}'.format(somma_col2), font=('TkDefaultFont', 24))
        self.somma_col2_label.grid(row=0, column=1, padx=10)

        pie_chart_caption = tk.Label(main_frame, text='2) Grafico clienti e pezzi', font=('TkDefaultFont', 24))
        pie_chart_caption.grid(row=4, column=0, pady=10, padx=20)

        pie_chart_button = ctk.CTkButton(main_frame, text='Mostra grafico', command=self.show_pie_chart)
        pie_chart_button.grid(row=4, column=1, pady=20, padx=20)

        giacenza_frame = tk.Frame(main_frame)
        giacenza_frame.grid(row=5, column=0, pady=10, padx=20, columnspan=2)
        self.avarage_days = 0
        self.update_clients_data()
        grouped_data, self.avarage_days = self.day_indicator()
        tk.Label(giacenza_frame, text='3) Tempo medio di invio ordine:', font=('TkDefaultFont', 24)).grid(row=0, column=0, padx=10)
        self.giacenza_label = tk.Label(giacenza_frame, text='{:.2f} giorni'.format(self.avarage_days), font=('TkDefaultFont', 24))
        self.giacenza_label.grid(row=0, column=1, padx=10)

        bar_chart_caption = tk.Label(main_frame, text="4) Tempo medio invio ordine per mese", font=("TkDefaultFont", 24))
        bar_chart_caption.grid(row=6, column=0, pady=10, padx=20)

        bar_chart_button = ctk.CTkButton(main_frame, text="Mostra grafico", command=self.show_bar_chart)
        bar_chart_button.grid(row=6, column=1, pady=20, padx=20)

        media_pezzi_venduti_frame = tk.Frame(main_frame)
        media_pezzi_venduti_frame.grid(row=7, column=0, pady=10, padx=20, columnspan=2)
        media_pezzi_venduti = self.media_pezzi_venduti()
        tk.Label(media_pezzi_venduti_frame, text="5) Media pezzi venduti per ordine:", font=("TkDefaultFont", 24)).grid(row=0, column=0, padx=10)
        self.media_pezzi_venduti_label = tk.Label(media_pezzi_venduti_frame, text="{:.2f}".format(media_pezzi_venduti), font=("TkDefaultFont", 24))
        self.media_pezzi_venduti_label.grid(row=0, column=1, padx=10)

        moving_average_caption = tk.Label(main_frame, text="6) Grafico pezzi venduti ogni mese", font=("TkDefaultFont", 24))
        moving_average_caption.grid(row=8, column=0, pady=10, padx=20)

        moving_average_button = ctk.CTkButton(main_frame, text="Mostra grafico", command=self.show_totali_pezzi_venduti_chart)
        moving_average_button.grid(row=8, column=1, pady=20, padx=20)

        update_button = ctk.CTkButton(main_frame, text='Aggiorna Indicatori', command=self.update_indicators)
        update_button.grid(row=9, column=0, pady=20, padx=20)

        back_button = ctk.CTkButton(main_frame, text='Torna alla Homepage', command=lambda: controller.show_frame(HomePage))
        back_button.grid(row=9, column=1, pady=50, padx=20)

    def update_expenses_data(self, start_date=None, end_date=None):
        start_date_str = self.start_date.get()
        end_date_str = self.end_date.get()

        if start_date_str and end_date_str:
            try:
                start_date = datetime.datetime.strptime(start_date_str, "%d/%m/%Y")
                end_date = datetime.datetime.strptime(end_date_str, "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Errore", "Formato data non valido. Si prega di utilizzare il formato 'dd/mm/yyyy'.")
                return
        else:
            start_date = None
            end_date = None

        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet1 = sheet.get_worksheet(0)
        expenses_data_all = sheet1.get_all_values()

        if start_date and end_date:
            self.expenses_data = [row for row in expenses_data_all if row[0] and datetime.datetime.strptime(row[0], "%d/%m/%Y") >= start_date and datetime.datetime.strptime(row[0], "%d/%m/%Y") <= end_date]
        else:
            self.expenses_data = expenses_data_all

    def get_sum_of_column_2(self):
        col_values = [row[1] for row in self.expenses_data]
        return sum(float(val) for val in col_values if val)
    
    def update_clients_data(self, start_date=None, end_date=None):
        gc = GoogleSheetAuth.get_instance().get_credentials()
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1) 
        if start_date is None:
            start_date = date.min

        if end_date is None:
            end_date = date.max

        self.clients_data = [row for row in sheet2.get_all_values() if start_date <= datetime.strptime(row[2], "%d/%m/%Y").date() <= end_date]

    def update_indicators(self):
        start_date = self.date_start.get_date()
        end_date = self.date_end.get_date()

        self.update_expenses_data(start_date, end_date)
        self.update_clients_data(start_date, end_date)
        somma_col2 = self.get_sum_of_column_2()
        self.somma_col2_label.config(text='€ {:.2f}'.format(somma_col2))
        grouped_data, self.avarage_days = self.day_indicator()
        self.giacenza_label.config(text='{:.2f} giorni'.format(self.avarage_days))
        media_pezzi_venduti = self.media_pezzi_venduti()
        self.media_pezzi_venduti_label.config(text="{:.2f}".format(media_pezzi_venduti))

    def show_pie_chart(self):
        start_date = self.date_start.get_date()
        end_date = self.date_end.get_date()
        self.update_clients_data(start_date, end_date)
        grouped_data, _ = self.day_indicator()  
        labels = list(grouped_data.keys())
        sizes = list(grouped_data.values())

        if sum(sizes) == 0:
            messagebox.showinfo("Non ci sono ordini", "Non ci sono ordini in questo periodo selezionato")
        else:
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
            plt.axis('equal')
            plt.title('Distribuzione pezzi venduti per cliente')
            plt.show()
  
    def get_data(self):
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(SAMPLE_SPREADSHEET_ID_input)
        sheet2 = sheet.get_worksheet(1)  
        return sheet2.get_all_values()
    
    def day_indicator(self):
        grouped_data = {}
        total_days = 0
        totale_ordini = 0

        for row in self.clients_data:
            client = row[0]
            pezzi_venduti = int(row[1])
            if row[2].strip() == "" or row[3].strip() == "":
                continue
            try:
                entry_date = datetime.strptime(row[2], "%d/%m/%Y")
            except ValueError:
                continue

            try:
                exit_date = datetime.strptime(row[3], "%d/%m/%Y")
            except ValueError:
                continue

            days_difference = (exit_date - entry_date).days
            if days_difference < 0:
                days_difference = 0

            total_days += days_difference
            totale_ordini += 1
            if client in grouped_data:
                grouped_data[client] += pezzi_venduti
            else:
                grouped_data[client] = pezzi_venduti

        if totale_ordini == 0:
            average_days = 0
        else:
            average_days = total_days / totale_ordini

        return grouped_data, average_days
    
    def media_pezzi_venduti(self):
        totale_pezzi_venduti = 0
        totale_ordini = 0
        
        for row in self.clients_data:
            pezzi = int(row[1])
            totale_pezzi_venduti += pezzi
            totale_ordini += 1
            
        if totale_ordini > 0:
            media_pezzi_venduti = totale_pezzi_venduti / totale_ordini
        else:
            media_pezzi_venduti = 0
        
        return media_pezzi_venduti

    def show_bar_chart(self):
        self.update_clients_data()
        months, average_delivery_times = self.tempo_mese()

        y_pos = np.arange(len(months))
        plt.bar(y_pos, average_delivery_times, align='center', alpha=0.5)
        plt.xticks(y_pos, months, rotation='vertical')
        plt.ylabel('Tempo medio (giorni)')
        plt.title('Tempo medio tra ricezione dell\'ordine e spedizione per mese')
        plt.tight_layout()
        plt.show()

    def tempo_mese(self):
        monthly_data = {}
        for row in self.clients_data:
            if row[2].strip() == "" or row[3].strip() == "":
                continue
            try:
                entry_date = datetime.strptime(row[2], "%d/%m/%Y")
                exit_date = datetime.strptime(row[3], "%d/%m/%Y")
            except ValueError:
                continue

            days_difference = (exit_date - entry_date).days
            if days_difference < 0:
                days_difference = 0

            month = entry_date.strftime("%Y-%m")
            if month in monthly_data:
                monthly_data[month]["total_days"] += days_difference
                monthly_data[month]["total_orders"] += 1
            else:
                monthly_data[month] = {"total_days": days_difference, "total_orders": 1}

        months = sorted(monthly_data.keys())
        average_delivery_times = [monthly_data[month]["total_days"] / monthly_data[month]["total_orders"] for month in months]

        return months, average_delivery_times
    
    def totali_pezzi_venduti_mensili(self):
        months_data = {}
        
        for row in self.clients_data:
            if row[2].strip() == "":
                continue
            try:
                entry_date = datetime.strptime(row[2], "%d/%m/%Y")
            except ValueError:
                continue

            pezzi_venduti = int(row[1])
            month = entry_date.strftime("%m/%Y")
            if month in months_data:
                months_data[month]["pezzi_venduti"] += pezzi_venduti
            else:
                months_data[month] = {"pezzi_venduti": pezzi_venduti}

        months = sorted(months_data.keys())
        pezzi_venduti_mensili = [months_data[month]["pezzi_venduti"] for month in months]
        return months, pezzi_venduti_mensili
        

    def show_totali_pezzi_venduti_chart(self):
        self.update_clients_data()
        months, pezzi_venduti_mensili = self.totali_pezzi_venduti_mensili()

        plt.plot(months, pezzi_venduti_mensili, marker='o', linestyle='-', label='Pezzi venduti mensili')
        plt.xticks(rotation='vertical')
        plt.ylabel('Pezzi venduti')
        plt.title('Pezzi venduti per mese')
        plt.legend()
        plt.tight_layout()
        plt.show()
        
if __name__ == '__main__':
    root = tk.Tk()
    ex = MyApp(root)
    root.mainloop()
    