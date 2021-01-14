

from tkinter import ttk, Tk, StringVar, END, N, S, E, W, DISABLED
from tkinter.scrolledtext import *
from timekeeper.ReportEdit import ReportEditApp
from timekeeper.Popups import PopConfirm
import time


class MainApp(): ### Main application window gui elements, data, and methods ###

    def __init__(self, db):
        self.db = db
        self.report_edit_window = None

        self.root = Tk()
        self.root.title('Time Keeper')
        self.root.resizable(False, False)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        self.selection = StringVar(self.root)

        new_shift_label = ttk.Label(self.frame, text = 'Start a new shift:')
        self.start_button = ttk.Button(self.frame, text = 'New Shift', command = self.start_new_shift, width = 8)

        add_job_label = ttk.Label(self.frame, text = 'Add a new job:')
        self.job_entry = ttk.Entry(self.frame)
        self.add_button = ttk.Button(self.frame, text = 'Add Job', command = self.add_job, width = 8)
        self.report_edit = ttk.Button(self.frame, text = 'Report and Edit', command = self.launch_report_edit)
        self.recover_label = ttk.Label(self.frame, text = 'Recover Shift(0)')

        new_shift_label.grid(column = 1, row = 1, pady = (5, 2), sticky = W)
        self.start_button.grid(column = 2, row = 2, sticky = E)
        add_job_label.grid(column = 1, row = 3, pady = (5, 2), sticky = W)
        self.job_entry.grid(column = 1, row = 4, sticky = (W, E))
        self.add_button.grid(column = 2, row = 4, sticky = E)
        self.report_edit.grid(column = 1, row = 5, pady = 5, sticky = W)
        self.recover_label.grid(column = 2, row = 5, pady = 5, sticky = W)
        
        self.frame.grid(column = 0, row = 0, padx = 5, pady = 0)
        self.container.grid(column = 0, row = 0)
        
        self.load_view()
    
    def load_view(self):
        #load job menu
        self.choices = self.db.get_jobs()
        self.job_menu = ttk.OptionMenu(self.frame, self.selection, 'Choose Job', *self.choices)
        self.job_menu.grid(column = 1, row = 2, sticky = W+E)
        self.selection.set('Choose Job')

        # check for incomplete shifts to recover
        recovered = self.db.check_incomplete()
        if recovered:
            self.recover_label["text"] = f"Recovered({recovered})"
        else:
            self.recover_label["text"] = ''

    def add_job(self):
        job_name = self.job_entry.get()
        if job_name not in self.choices and job_name != '':
            self.job_entry.delete(0, END)
            self.db.add_job(job_name)
            self.load_view()

    def start_new_shift(self):
        job_name = self.selection.get()
        if job_name in self.choices:
            self.load_view()
            shift_window = ShiftApp(self.db, job_name)
            shift_window.root.mainloop()
    
    def launch_report_edit(self):
        self.report_edit_window = ReportEditApp(self.db)
        self.report_edit_window.root.mainloop()


class ShiftApp(): ### In-progress Shift application window gui elements, data, and methods ###

    def __init__(self, db, job_name):
        self.db = db
        self.events = {}

        self.job_name = job_name
        self.start_time = time.time()
        self.break_start = 0
        self.break_time = 0
        self.id = self.db.add_shift(self.job_name, self.start_time, None, self.break_time, None)
        print(self.id)

        self.root = Tk()
        self.root.title(f'Shift - {job_name}')
        self.root.resizable(False, False)
        self.root.overrideredirect(0)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        self.job_label = ttk.Label(self.frame, text = f'Job: {job_name}')
        self.elapsed_time_label = ttk.Label(self.frame, width = 18)
        self.button_frame = ttk.Frame(self.frame)
        self.pause_button = ttk.Button(self.button_frame, text = 'Pause', command = self.toggle_break, width = 7)
        self.save_button = ttk.Button(self.button_frame, text = 'Stop and Save', command = self.end_prompt)
        self.cancel_button = ttk.Button(self.frame, text = 'Cancel', command = self.cancel_prompt)
        self.notes = ScrolledText(self.frame, width = 60, height = 15, relief = 'sunken')
        # TODO: Add 'Prior Shifts' button that links to 'self.launch_report_edit'
        self.report_job_button = ttk.Button(self.frame, text = 'Prior Shifts', command = self.launch_report_edit)

        self.job_label.grid(column = 1, columnspan = 2, row = 1, sticky = W, pady = 5)
        self.elapsed_time_label.grid(column = 3, row = 1, sticky = E)
        self.button_frame.grid(column = 1, columnspan = 2, row = 2, sticky = W)
        self.pause_button.grid(column = 1, row = 1, sticky = W)
        self.save_button.grid(column = 2, row = 1, sticky = W)
        self.cancel_button.grid(column = 3, row = 2, sticky = E)
        self.notes.grid(column = 1, columnspan = 3, row = 3, pady = (5, 5))
        self.report_job_button.grid(column = 1, row = 4, sticky = W)
        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid(column = 0, row = 0)

        self.root.protocol("WM_DELETE_WINDOW", self.cancel_prompt)

        self.time_counter()
        self.auto_save()
    
    def time_counter(self):
        if not self.break_start:
            elapsed_time = time.gmtime(time.time() - self.start_time - self.break_time)
            elapsed_hours = time.strftime('%H', elapsed_time)
            elapsed_minutes = time.strftime('%M', elapsed_time)
            elapsed_seconds = time.strftime('%S', elapsed_time)
            self.elapsed_time_label['text'] = f'Elapsed Time: {elapsed_hours}:{elapsed_minutes}:{elapsed_seconds}'
        self.events['time_counter'] = self.root.after(200, self.time_counter)
    
    def auto_save(self):
        self.save_update()
        self.events['auto_save'] = self.root.after(5000, self.auto_save)

    def toggle_break(self):
        if not self.break_start:
            self.break_start = time.time()
            self.job_label['text'] = f'{self.job_name} - Paused'
            self.pause_button['text'] = 'Resume'
        else:
            self.break_time += time.time() - self.break_start
            self.break_start = 0
            self.job_label['text'] = self.job_name
            self.pause_button['text'] = 'Pause'
    
    def save_update(self):
        if self.break_start:
            break_time = self.break_time + (time.time() - self.break_start)
        else:
            break_time = self.break_time
        end_time = time.time()
        notes = self.notes.get(1.0, END)
        self.db.update_shift(self.id, end_time, break_time, notes)

    def end_prompt(self):
        popup = PopConfirm("Save and exit shift?", self.end_shift)
        popup.root.mainloop()
    
    def cancel_prompt(self):
        popup = PopConfirm("Cancel and delete shift?", self.cancel_shift)
        popup.root.mainloop()

    def end_shift(self):
        self.save_update()
        self.db.complete_shift(self.id)
        self.close()
    
    def cancel_shift(self):
        self.db.remove_shift(self.id)
        self.close()
    
    def launch_report_edit(self):
        self.report_edit_window = ReportEditApp(self.db, job_name = self.job_name)
        self.report_edit_window.root.mainloop()
    
    def close(self):
        for val in self.events.values():
            # print("Canceling command:", val)
            self.root.after_cancel(val)
        self.root.destroy()
