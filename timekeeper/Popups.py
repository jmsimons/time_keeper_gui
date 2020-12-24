from tkinter import ttk, Tk, N, S, E, W

class PopConfirm:

    def __init__(self, message, confirm_func):
        self.confirm_func = confirm_func
        self.root = Tk()
        self.root.title("Confirm")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)
        self.root.grab_set()

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        label = ttk.Label(self.frame, text = message)
        canel_button = ttk.Button(self.frame, text = "Cancel", command = self.root.destroy)
        confirm_button = ttk.Button(self.frame, text = "Confirm", command = self.confirm_close)
        confirm_button.focus_set()

        label.grid(column = 1, columnspan = 3, row = 1, rowspan = 2, padx = 5, pady = (10, 5))
        canel_button.grid(column = 2, row = 3, sticky = E)
        confirm_button.grid(column = 3, row = 3, sticky = E)

        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid()
    
    def confirm_close(self):
        self.confirm_func()
        self.root.destroy()

class PopAlert:

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