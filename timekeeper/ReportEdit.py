
from tkinter import ttk, Tk, StringVar, END, N, S, E, W, NORMAL, DISABLED
from tkinter.scrolledtext import ScrolledText
import time, clipboard
from timekeeper.grid_table import GridTable
from timekeeper.Export import Export
from timekeeper.Popups import PopConfirm, EntryBox


class ReportEditApp(): ### 'Report hours' and 'edit jobs/shifts' application window gui elements, data, and methods ###
    
    def __init__(self, db, **kwargs):
        self.db = db

        self.root = Tk()
        self.root.title('Report and Edit')
        # self.root.geometry("600x400")
        self.root.resizable(False, False)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)
        self.grid_configure()
        
        filter_label = ttk.Label(self.frame, text = "Filter:")
        self.view_selection = StringVar(self.root)
        self.job_selection = StringVar(self.root)
        self.start_selection = StringVar(self.root)
        self.end_selection = StringVar(self.root)
        self.export_selection = StringVar(self.root)
        self.build_menus()
        self.search_input = ttk.Entry(self.frame, width = 16)#, placeholder = 'Search Notes...'

        self.totals_label = ttk.Label(self.frame, text = 'Hours: \tShifts:')
        self.table_frame = ttk.Frame(self.frame)
        self.build_table(**kwargs)
        self.build_date_select()

        export_options = ('Text', 'PDF')
        self.export_menu = ttk.OptionMenu(self.frame, self.export_selection, 'Export', *export_options)
        self.view_shift_button = ttk.Button(self.frame, text = 'View/Edit Shift', command = self.view_item)

        filter_label.grid(column = 1, row = 1, sticky = W, pady = 5)
        self.view_menu.grid(column = 2, row = 1, sticky = E)
        self.job_menu.grid(column = 1, columnspan = 2, row = 2, sticky = (W, E))
        self.search_input.grid(column = 5, row = 2, sticky = (W, E))
        self.totals_label.grid(column = 1, columnspan = 5, row = 4, sticky = W, pady = 5)
        self.table_frame.grid(column = 1, columnspan = 5, row = 5, sticky = (N, S, E, W))
        self.export_menu.grid(column = 1, columnspan = 2, row = 6, sticky = W)
        self.view_shift_button.grid(column = 5, row = 6, sticky = E, pady = 5)

        self.frame.grid(column = 0, row = 0, padx = 5, sticky = (N, S, E, W))
        self.container.grid(column = 0, row = 0, sticky = (N, S, E, W))

        self.view_menu.bind("<ButtonRelease-1>", self.build_table)
        self.job_menu.bind("<ButtonRelease-1>", self.filter_data)
        self.per_start_menu.bind("<ButtonRelease-1>", self.filter_data)
        self.per_end_menu.bind("<ButtonRelease-1>", self.filter_data)
        self.search_input.bind('<KeyRelease>', self.filter_data)
        self.search_input.bind("<Return>", self.filter_data)
        self.export_menu.bind("<ButtonRelease-1>", self.export)
    
    def grid_configure(self):
        # TODO: this isn't working, trying to figure out why. The goal is to set fixed column-widths so that the ui doesn't redraw when a widget changes size.
        self.root.columnconfigure(0, weight = 0)
        self.container.columnconfigure(0, weight = 0)
        self.frame.columnconfigure(0, weight = 0)
        self.frame.columnconfigure(1, weight = 1)
        self.frame.columnconfigure(2, weight = 2)
        self.frame.columnconfigure(3, weight = 2)
        self.frame.columnconfigure(4, weight = 2)
        self.frame.columnconfigure(5, weight = 2)

    def build_menus(self):
        self.job_choices = ['All Jobs'] + self.db.report_jobs()
        self.job_menu = ttk.OptionMenu(self.frame, self.job_selection, 'All Jobs', *self.job_choices)
        self.job_menu.config(width = 10)

        self.view_choices = ("Shifts", "Tasks", "Jobs")
        self.view_menu = ttk.OptionMenu(self.frame, self.view_selection, self.view_choices[0], *self.view_choices)
        self.job_menu.config(width = 5)
    
    def build_table(self, event = None, **kwargs):
        self.table_view = ttk.Treeview(self.table_frame, selectmode = 'browse')
        vbar = ttk.Scrollbar(self.table_frame, orient = 'vertical', command = self.table_view.yview)
        self.table_view.config(yscrollcommand = vbar.set)
        self.table_view.grid(column = 1, columnspan = 1, row = 1, sticky = (N, S, E, W))
        vbar.grid(column = 2, row = 1, sticky = (N, S))

        view_selection = self.view_selection.get()
        if view_selection == self.view_choices[0]:
            self.job_menu.config(state = NORMAL)
            self.shifts_table()
        elif view_selection == self.view_choices[1]:
            self.job_menu.config(state = NORMAL)
            self.tasks_table()
        elif view_selection == self.view_choices[2]:
            # self.job_menu set to 'All Jobs'
            self.job_menu.config(state = DISABLED)
            self.jobs_table()
        self.tid_lookup = {}
        self.get_rows(**kwargs)
        self.populate_table()
        self.table_view.bind("<Double-Button-1>", self.view_item)

    def shifts_table(self):
        self.table_view['columns'] = ('1', '2', '3', '4', '5')
        self.table_view['show'] = 'headings'
        self.table_view.column('1', width = 120, anchor = 'w')
        self.table_view.column('2', width = 80, anchor = 'w')
        self.table_view.column('3', width = 70, anchor = 'w')
        self.table_view.column('4', width = 40, anchor = 'w')
        self.table_view.column('5', width = 150, anchor = 'w')
        self.table_view.heading('1', text = 'Job')
        self.table_view.heading('2', text = 'Date')
        self.table_view.heading('3', text = 'Start')
        self.table_view.heading('4', text = 'Hours')
        self.table_view.heading('5', text = 'Notes')
    
    def tasks_table(self):
        self.table_view['columns'] = ('1', '2', '3', '4')
        self.table_view['show'] = 'headings'
        self.table_view.column('1', width = 120, anchor = 'w')
        self.table_view.column('2', width = 80, anchor = 'w')
        self.table_view.column('3', width = 100, anchor = 'w')
        self.table_view.column('4', width = 160, anchor = 'w')
        self.table_view.heading('1', text = 'Job')
        self.table_view.heading('2', text = 'Date')
        self.table_view.heading('3', text = 'Created')
        self.table_view.heading('4', text = 'Title')
    
    def jobs_table(self):
        self.table_view['columns'] = ('1', '2', '3', '4')
        self.table_view['show'] = 'headings'
        self.table_view.column('1', width = 120, anchor = 'w')
        self.table_view.column('2', width = 80, anchor = 'w')
        self.table_view.column('3', width = 100, anchor = 'w')
        self.table_view.column('4', width = 160, anchor = 'w')
        self.table_view.heading('1', text = 'Job')
        self.table_view.heading('2', text = 'Date')
        self.table_view.heading('3', text = 'Created')
        self.table_view.heading('4', text = 'Shifts')
    
    def build_date_select(self):
        format = '%Y/%m/%d'
        # TODO: Replace 17 hour offset with time zone setting from config
        start = int(self.shifts[0]['start'] / 86400) * 86400 - (17 * 3600)
        end = int(time.time() / 86400 + 1) * 86400 - (17 * 3600) + (24 * 3600) + 1
        self.seconds_range = [i for i in range(start, end, 86400)][::-1]
        self.date_range = [time.strftime(format, time.localtime(i)) for i in self.seconds_range]
        self.per_start_menu = ttk.OptionMenu(self.frame, self.start_selection, self.date_range[0], *self.date_range)
        self.per_end_menu = ttk.OptionMenu(self.frame, self.end_selection, self.date_range[0], *self.date_range)
        self.start_selection.set(self.date_range[-1])
        self.end_selection.set(self.date_range[0])

        self.per_start_menu.grid(column = 3, row = 2, sticky = (W, E))
        self.per_end_menu.grid(column = 4, row = 2, sticky = (W, E))

    def filter_data(self, event = None):
        # print("Filtering Data...")
        job_name = self.job_selection.get()
        if job_name == self.job_choices[0]:
            job_name = None
        period_start = self.start_selection.get()
        period_start = self.seconds_range[self.date_range.index(period_start)]
        period_end = self.end_selection.get()
        period_end = self.seconds_range[self.date_range.index(period_end)]
        search_term = self.search_input.get()
        if search_term.strip() == '': search_term = None
        self.clear_table()
        self.get_rows(job_name = job_name, period_start = period_start, period_end = period_end, search_term = search_term)
        self.populate_table()

    def get_rows(self, **kwargs):
        view_selection = self.view_selection.get()
        if view_selection == self.view_choices[0]:
            self.get_shifts(**kwargs)
        elif view_selection == self.view_choices[1]:
            self.get_tasks(**kwargs)
        elif view_selection == self.view_choices[2]:
            self.get_jobs()
        if not "job_name" in kwargs or not kwargs["job_name"]:
            job_name = 'All Jobs'
        else:
            job_name = kwargs["job_name"]
        self.job_selection.set(job_name)
        self.total_shifts = len(self.shifts)
        self.total_hours = sum([i['hours'] for i in self.shifts])
        self.total_hours = round(self.total_hours, 2)

    def get_shifts(self, **kwargs):
        self.shifts = self.db.report_shifts(**kwargs)
        self.table_items = []
        for shift in self.shifts:
            if len(shift['notes']) < 20:
                notes = shift['notes']
            else:
                notes = shift['notes'][:20].split('\n')[0]
            start = shift['str_start'].split()
            self.table_items.append((shift["id"], (shift['job'], start[0], start[1], shift['hours'], notes)))
    
    def get_tasks(self, **kwargs):
        tasks = self.db.report_tasks(**kwargs)
        self.table_items = [(i["id"], (i["job_name"], i["time_created"].split()[0], i["time_created"].split()[1], i["title"])) for i in tasks]

    def get_jobs(self):
        jobs = self.db.report_jobs(return_dict = True)
        self.table_items = []
        for job in jobs:
            total_shifts = len(self.db.report_shifts(job_name = job["name"]))
            self.table_items.append((job["id"], (job["name"], job["created"].split()[0], job["created"].split()[1], total_shifts)))

    def populate_table(self):
        self.totals_label['text'] = f'Hours: {self.total_hours}\tShifts: {self.total_shifts}'
        for item in self.table_items[::-1]:
            tid = self.table_view.insert('', 'end', values = item[1])
            self.tid_lookup[tid] = item[0]
    
    def clear_table(self):
        # print("Clearing Table...")
        for tid in self.tid_lookup:
            self.table_view.delete(tid)
        self.tid_lookup = {}

    def export(self, event = None):
        doc_type = self.export_selection.get()
        self.export_selection.set('Export')
        job_selection = self.job_selection.get()
        period_start = self.start_selection.get()
        period_end = self.end_selection.get()
        search_term = self.search_input.get()
        if search_term in ('', ' '): search_term = None
        export_shifts = [i for i in self.shifts]
        for shift in export_shifts:
            shift["tasks"] = self.db.report_tasks(shift_id = shift["id"])
        Export(doc_type, job_selection, period_start, period_end, search_term, self.total_hours, export_shifts)

    def view_item(self, event = None):
        try: tid = self.table_view.focus()
        except: return
        item_type = self.view_selection.get().lower().rstrip('s')
        item_id = self.tid_lookup[tid]
        if item_type == "shift":
            item = self.db.get_shift(item_id)
        elif item_type == "task":
            item = self.db.get_task(item_id)
        elif item_type == "job":
            item = self.db.get_job(item_id)
        print("Viewing", item_type, item_id)
        item_view = ViewEditPane(self, item_type, item)
        item_view.root.mainloop()


class ViewEditPane():

    def __init__(self, ReportEdit, item_type, item_dict):
        self.report_edit = ReportEdit
        self.item_type = item_type
        self.item = item_dict
        self.root = Tk()
        title = f"{item_type.capitalize()} Record"
        self.root.title(title)
        self.root.resizable(False, False)
        # self.root.overrideredirect(True)

        self.edit_selection = StringVar(self.root)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)
        self.edit_frame = ttk.Frame(self.frame)

        if self.item_type == "shift": self.load_shift()
        elif self.item_type == "task": self.load_task()
        elif self.item_type == "job": self.load_job()
        self.delete_button = ttk.Button(self.edit_frame, text = 'Delete Shift', command = self.delete_prompt)
        self.done_button = ttk.Button(self.frame, text = 'Done', command = self.root.destroy)
        self.edit_menu = ttk.OptionMenu(self.edit_frame, self.edit_selection, 'Edit', *self.edit_options)
        self.edit_menu.grid(column = 1, row = 1, sticky = W)
        self.delete_button.grid(column = 2, row = 1, sticky = E)
        self.done_button.grid(column = 2, row = 5, sticky = E)
        self.edit_frame.grid(column = 1, row = 5, sticky = W)
        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid()

        self.root.bind("<Command-c>", self.copy_notes)
        self.edit_menu.bind("<ButtonRelease-1>", self.edit_item)

    def load_shift(self): ## Load Shift view elements ##
        self.job_label = ttk.Label(self.frame)
        self.start_label = ttk.Label(self.frame)
        self.end_label = ttk.Label(self.frame)
        self.break_label = ttk.Label(self.frame)
        self.hours_label = ttk.Label(self.frame)
        self.notes = ScrolledText(self.frame, width = 60, height = 15, relief = 'sunken')

        self.job_label.grid(column = 1, row = 1, sticky = W, ipadx = 2)
        self.start_label.grid(column = 1, row = 2, sticky = W, ipadx = 5, pady = 2)
        self.end_label.grid(column = 1, row = 3, sticky = W, ipadx = 5, ipady = 0)
        self.break_label.grid(column = 2, row = 2, sticky = W, ipadx = 5, ipady = 0)
        self.hours_label.grid(column = 2, row = 3, sticky = W, ipadx = 5, ipady = 0)
        self.notes.grid(column = 1, columnspan = 2, row = 4, sticky = (N, S, E, W), pady = 5)

        self.edit_options = ('Job', 'Start', 'End', 'Break', 'Notes')
        self.job_label['text'] = f"Job:\t{self.item['job']}"
        self.start_label['text'] = f"Start:\t{self.item['str_start']}"
        self.end_label['text'] = f"End:\t{self.item['str_end']}"
        self.break_label['text'] = f"Break:\t{self.item['break']} (minutes)"
        self.hours_label['text'] = f"Hours:\t{self.item['hours']}"
        self.notes.config(state = NORMAL)
        self.notes.delete('1.0', END)
        self.notes.insert(END, self.item['notes'])
        self.notes.config(state = DISABLED)
    
    def load_task(self): ## Loas Task view elements ##
        self.notes = ScrolledText(self.frame, width = 60, height = 15, relief = 'sunken')

        self.notes.grid(column = 1, columnspan = 2, row = 4, sticky = (N, S, E, W), pady = 5)
        self.edit_options = ("Title", "Notes")
        self.notes.config(state = NORMAL)
        self.notes.delete('1.0', END)
        self.notes.insert(END, self.item['notes'])
        self.notes.config(state = DISABLED)

    def load_job(self): ## Load Job view elements ##
        self.edit_options = ("Name")

    def edit_item(self, event):
        key = self.edit_selection.get().lower()
        if key == 'edit': return
        self.edit_selection.set('Edit')
        if self.item_type == "shift":
            if key in ('start', 'end'):
                key = 'str_' + key
        elif self.item_type == "task": pass
        elif self.item_type == "job": pass
        print(self.item)
        entry = EntryBox(self.save_property, key, self.item[key])
        entry.root.mainloop()
    
    def save_property(self, key, value):
        if self.item_type == "shift":
            self.item = self.report_edit.db.update_shift_field(self.item['id'], key, value)
            self.load_shift()
        elif self.item_type == "task":
            self.item = self.report_edit.db.update_task_field(self.item['id'], key, value)
            self.load_task()
        elif self.item_type == "job":
            self.item = self.report_edit.db.update_job_field(self.item['id'], key, value)
            self.load_job()
        self.report_edit.filter_data()
    
    def copy_notes(self, event = None):
        clipboard.copy(self.notes.get(1.0, END))
        print('Notes Copied')
    
    def delete_prompt(self):
        popup = PopConfirm("Permanently delete shift?", self.delete_shift)
        popup.root.mainloop()
    
    def delete_shift(self):
        self.report_edit.db.remove_shift(self.item['id'])
        self.root.destroy()
        self.report_edit.filter_data()


class ViewEditJob: # View-pane for Job

    def __init__(self):
        pass

    def edit_job(self):
        pass

    def delete_prompt(self):
        pass

    def delete_job(self):
        pass