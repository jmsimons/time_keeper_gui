from tkinter import ttk, Tk, StringVar, Listbox, MULTIPLE, SINGLE, END, N, S, E, W, DISABLED, TclError
from tkinter.scrolledtext import ScrolledText
from timekeeper.report_edit import ReportEditApp
from timekeeper.popups import PopConfirm
import time


class MainApp(): ### Main application window ###

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
        self.choices = self.db.report_jobs()
        self.job_menu = ttk.OptionMenu(self.frame, self.selection, 'Choose Job', *self.choices)
        self.job_menu.grid(column = 1, row = 2, sticky = W+E)
        self.selection.set('Choose Job')

        # check for incomplete shifts to recover #
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


class ShiftApp(): ### In-progress Shift application ###

    def __init__(self, db, job_name):
        self.db = db
        self.events = {}

        self.job_name = job_name
        self.start_time = time.time()
        self.break_start = 0
        self.break_time = 0
        self.id = self.db.add_shift(self.job_name, self.start_time, None, self.break_time, None)
        self.tasks = {}
        self.task_index = []
        self.cur_task = 0

        self.root = Tk()
        self.root.title(f'Shift - {job_name}')
        self.root.resizable(False, False)
        self.root.overrideredirect(0)

        self.tm1_selection = StringVar(self.root)
        self.tm2_selection = StringVar(self.root)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        self.job_label = ttk.Label(self.frame, text = f'Job: {job_name}')
        self.elapsed_time_label = ttk.Label(self.frame, width = 18)

        self.task_frame = ttk.Frame(self.frame)
        self.task_label = ttk.Label(self.task_frame, text = "Tasks:")
        self.tm1_options, self.tm2_options = ('All Job Tasks', 'Shift Tasks Only'), ()
        self.task_menu1 = ttk.OptionMenu(self.frame, self.tm1_selection, self.tm1_options[0], *self.tm1_options)
        self.task_entry = ttk.Entry(self.frame)
        self.task_list = Listbox(self.task_frame, selectmode = SINGLE, width = 20, height = 12, relief = 'sunken')
        vbar = ttk.Scrollbar(self.task_frame, orient = 'vertical', command = self.task_list.yview)
        self.task_list.config(yscrollcommand = vbar.set)
        self.new_task_button = ttk.Button(self.frame, text = "New Task", command = self.new_task)

        self.button_frame = ttk.Frame(self.frame)
        self.pause_button = ttk.Button(self.button_frame, text = 'Pause', command = self.toggle_break, width = 7)
        # TODO: Add info button
        self.cancel_button = ttk.Button(self.frame, text = 'Cancel', command = self.cancel_prompt)
        self.notes = ScrolledText(self.frame, undo = True, width = 60, height = 15, relief = 'sunken')
        self.report_job_button = ttk.Button(self.frame, text = 'Prior Shifts', command = self.launch_report_edit)
        self.save_button = ttk.Button(self.frame, text = 'Stop and Save', command = self.end_prompt)

        self.job_label.grid(column = 2, columnspan = 2, row = 1, sticky = W, pady = 5)
        self.elapsed_time_label.grid(column = 4, row = 1, sticky = E)
        self.task_menu1.grid(column = 1, row = 1, sticky = (E, W), padx = (0, 15))
        self.task_entry.grid(column = 1, row = 2, sticky = (E, W), padx = (0, 15))
        self.task_list.grid(column = 1, row = 1, sticky = (N, S))
        vbar.grid(column = 2, row = 1, sticky = (N, S))
        self.task_frame.grid(column = 1, row = 3, sticky = (N, S), pady = (5, 5))
        self.new_task_button.grid(column = 1, row = 4, sticky = W)
        self.button_frame.grid(column = 2, columnspan = 2, row = 2, sticky = W)
        self.pause_button.grid(column = 2, row = 1, sticky = W)
        self.cancel_button.grid(column = 4, row = 2, sticky = E)
        self.notes.grid(column = 2, columnspan = 3, row = 3, pady = (5, 5))
        self.report_job_button.grid(column = 2, row = 4, sticky = W)
        self.save_button.grid(column = 4, row = 4, sticky = E)
        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid(column = 0, row = 0)

        self.root.protocol("WM_DELETE_WINDOW", self.cancel_prompt)
        self.task_menu1.bind("<ButtonRelease-1>", self.filter_tasks) # filter_tasks clears notes
        self.task_entry.bind("<KeyRelease>", self.filter_tasks)
        self.task_list.bind("<ButtonRelease-1>", self.focus_task)
        self.task_list.bind("<Double-Button-1>", self.copy_task_title)
        self.notes.bind("<Command-Z>", self.edit_undo)

        self.time_counter()
        self.auto_save()
        self.get_tasks()
    
    def edit_undo(self, event = None):
        try:
            self.notes.edit_undo()
        except TclError as e:
            print(e)

    def get_tasks(self, event = None, **kwargs): ## Gets set of filtered tasks from db ##
        if "Job" in self.tm1_selection.get():
            kwargs["job_name"] = self.job_name
        else:
            kwargs["shift_id"] = self.id
        tasks = self.db.report_tasks(**kwargs)
        self.tasks.clear()
        for task in tasks:
            self.tasks[task["id"]] = task
        self.task_list.delete(0, END)
        self.cur_task = 0
        self.task_index = []
        self.task_list.insert(END, "Shift Notes")
        self.task_index.append(None)
        for task in [i for i in self.tasks.values()][::-1]:
            self.task_list.insert(END, task['title'])
            self.task_index.append(task["id"])
    
    def filter_tasks(self, event = None):
        # TODO: set focus to 'Shift Notes'
        search_term = self.task_entry.get()
        if search_term in ('', ' '):
            search_term = None
        self.get_tasks(search_term = search_term)
        notes = self.db.get_shift(self.id)["notes"]
        self.notes.delete("0.0", END)
        self.notes.insert(END, notes)
    
    def new_task(self):
        task_title = self.task_entry.get()
        if task_title not in ('', ' '):
            task = self.db.add_task(self.id, self.job_name, task_title)
            self.task_entry.delete(0, END)
            self.get_tasks()
            self.task_list.activate(self.task_index.index(task["id"]))
    
    def focus_task(self, event = None): ## displays notes for the currently selected task ##
        if self.task_list.curselection():
            new_cur = self.task_list.curselection()[0]
            if new_cur == self.cur_task:
                return
            notes = self.notes.get(0.0, END).strip('\n')
            if self.cur_task: # if the notes being displayed belong to a task
                task_id = self.task_index[self.cur_task]
                self.tasks[task_id]["notes"] = notes
            else:
                self.db.update_shift(self.id, notes = notes)
            if new_cur: # if the new notes to be displayed belong to a task
                task_id = self.task_index[new_cur]
                notes = self.tasks[task_id]["notes"]
            else:
                shift = self.db.report_shifts(shift_id = self.id)[0]
                notes = shift["notes"]
            self.notes.delete('0.0', END)
            self.notes.insert(END, notes)
            self.cur_task = new_cur
    
    def copy_task_title(self, event = None): ## Copies title from current selection in task_list to task_entry ##
        cur = self.task_list.curselection()[0]
        if cur:
            task = self.tasks[self.task_index[cur]]
            self.task_entry.delete(0, END)
            self.task_entry.insert(0, task["title"])
            self.filter_tasks()
        
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
    
    def save_update(self): ## Commits current state for shift and tasks to db ##
        if self.break_start:
            break_time = self.break_time + (time.time() - self.break_start)
        else:
            break_time = self.break_time
        end_time = time.time()
        notes = self.notes.get(0.0, END).strip('\n')
        if self.cur_task: # if the notes being displayed belong to a task
            task_id = self.task_index[self.cur_task]
            self.tasks[task_id]["notes"] = notes
            notes = None
        self.db.update_shift(self.id, end_time = end_time, break_time = break_time, notes = notes)
        for _, task in self.tasks.items():
            self.db.update_task(**task)

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
            self.root.after_cancel(val)
        self.root.destroy()
