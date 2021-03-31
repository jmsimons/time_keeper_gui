from tkinter import ttk, Tk, Grid, N, S, E, W, END
from tkinter.scrolledtext import ScrolledText

class PopConfirm: ### General popup that displays a message pertaining to an action, allows the user to either confirm or cancel the action ###

    def __init__(self, message, confirm_func):
        self.confirm_func = confirm_func
        self.root = Tk()
        self.root.title("Confirm")
        # self.root.geometry("200x100")
        self.root.grab_set()

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)# , width = 200, height = 100
        self.grid_config()

        label = ttk.Label(self.frame, text = message)
        canel_button = ttk.Button(self.frame, text = "Cancel", command = self.root.destroy)
        confirm_button = ttk.Button(self.frame, text = "Confirm", command = self.confirm_close)
        confirm_button.focus_set()

        label.grid(column = 1, columnspan = 3, row = 1, rowspan = 2, padx = 5, pady = 10, sticky = W)
        canel_button.grid(column = 2, row = 3, sticky = (S, E))
        confirm_button.grid(column = 3, row = 3, sticky = (S, E))

        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5, sticky = (N, S, E, W))
        self.container.grid(column = 0, row = 0, sticky = (N, S, E, W))
        # self.container.pack(fill = "both", expand = True)
        
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
    
    def grid_config(self):
        Grid.columnconfigure(self.root, 0, weight = 1)
        Grid.rowconfigure(self.root, 0, weight = 1)
        Grid.columnconfigure(self.container, 0, weight = 1)
        Grid.rowconfigure(self.container, 0, weight = 1)
        for x in range(3):
            Grid.columnconfigure(self.frame, x, weight = 1)
        for y in range(3):
            Grid.rowconfigure(self.frame, y, weight = 1)
    
    def confirm_close(self):
        self.confirm_func()
        self.root.destroy()

class PopAlert: ### General popup that displays a message with 'OK' button ###

    def __init__(self, message, confirm_func = None):
        self.confirm_func = confirm_func
        self.root = Tk()
        self.root.title("Alert")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.grab_set()

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        label = ttk.Label(self.frame, text = message)
        ok_button = ttk.Button(self.frame, text = "OK", command = self.confirm_close)
        ok_button.focus_set()

        label.grid(column = 1, columnspan = 3, row = 1, rowspan = 2, padx = 5, pady = (10, 5))
        ok_button.grid(column = 3, row = 3, sticky = E)

        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid()
    
    def confirm_close(self):
        if self.confirm_func:
            self.confirm_func()
        self.root.destroy()


class EntryBox: ### Popup used by EditJobs and ViewEditShift to change a recorded property ###

    def __init__(self, SaveFunc, key, current):
        self.save_func = SaveFunc
        self.key = key
        self.current = current
        self.get_args = None

        self.root = Tk()
        self.root.title(f'Edit {key.capitalize()}')
        self.root.resizable(False, False)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        if key in ("job", "name", "title"): self.string_entry()
        elif 'start' in key or 'end' in key: self.time_entry()
        elif key == 'break': self.break_entry()
        elif key == 'notes': self.notes_entry()

        label_text = 'Current: '
        if key != 'notes': label_text += str(self.current)
        self.label = ttk.Label(self.frame, text = label_text)

        self.button_frame = ttk.Frame(self.frame)
        self.cancel_button = ttk.Button(self.button_frame, text = 'Cancel', command = self.root.destroy)
        self.save_button = ttk.Button(self.button_frame, text = 'Save', command = self.save_property)

        self.label.grid(column = 1, columnspan = 2, row = 1, sticky = W, pady = 0)
        self.entry.grid(column = 1, columnspan = 2, row = 2, pady = 5, ipadx = 7)#, sticky = (E, W)
        self.button_frame.grid(column = 1, columnspan = 2, row = 3)#, sticky = E
        self.cancel_button.grid(column = 1, row = 1)#, sticky = W
        self.save_button.grid(column = 2, row = 1)#, sticky = E
        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.pack()
    
    def float_mask(self, event):
        chars = self.entry.get()
        try:
            float(chars)
        except:
            self.entry.delete(len(chars) - 1, END)

    def time_mask(self, event):
        last = self.entry.get()
        try: int(last)
        except: self.entry.delete(len(last) - 1, END)
        if len(self.entry.get()) == 2:
            self.entry.insert(END,":")
        elif len(self.entry.get()) == 5:
            self.entry.insert(END,":")
        elif len(self.entry.get()) >= 9:
            self.entry.delete(8, END)
    
    def save_property(self):
        if self.get_args:
            value = self.entry.get(*self.get_args)
        else:
            value = self.entry.get()
        # TODO: some code that confirms the entry, maybe a popup notice with yes/no buttons
        self.save_func(self.key, value)
        self.root.destroy()
    
    def string_entry(self):
        self.entry = ttk.Entry(self.frame)
    
    def time_entry(self):
        self.entry = ttk.Entry(self.frame)
        self.entry.insert(END, self.current)
    
    def break_entry(self):
        self.entry = ttk.Entry(self.frame)
        self.entry.config(width = 4)
        self.entry.bind('<KeyRelease>', self.float_mask)

    def notes_entry(self):
        self.entry = ScrolledText(self.frame, width = 60, height = 15, relief = 'sunken')
        self.entry.insert(END, self.current)
        self.get_args = (1.0, END)