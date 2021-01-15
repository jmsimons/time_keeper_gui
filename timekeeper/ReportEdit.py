
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
        self.root.resizable(False, False)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)
        
        filter_label = ttk.Label(self.frame, text = 'Filter Shifts:')
        self.job_selection = StringVar(self.root)
        self.start_selection = StringVar(self.root)
        self.end_selection = StringVar(self.root)
        self.export_selection = StringVar(self.root)
        self.build_menu()
        self.get_data(**kwargs)
        self.build_date_select()
        self.search_input = ttk.Entry(self.frame, width = 16)#, placeholder = 'Search Notes...'
        self.filter_button = ttk.Button(self.frame, text = 'Filter', command = self.filter_data)

        self.totals_label = ttk.Label(self.frame, text = 'Hours: \tShifts:')
        self.table_frame = ttk.Frame(self.frame)
        self.table_view = ttk.Treeview(self.table_frame, selectmode = 'browse')
        vbar = ttk.Scrollbar(self.table_frame, orient = 'vertical', command = self.table_view.yview)
        self.table_view.config(yscrollcommand = vbar.set)
        self.table_view['columns'] = ('1', '2', '3', '4', '5')
        self.table_view['show'] = 'headings'
        self.table_view.column('1', width = 120, anchor = 'w')
        self.table_view.column('2', width = 80, anchor = 'w')
        self.table_view.column('3', width = 75, anchor = 'w')
        self.table_view.column('4', width = 45, anchor = 'w')
        self.table_view.column('5', width = 150, anchor = 'w')
        self.table_view.heading('1', text = 'Job')
        self.table_view.heading('2', text = 'Date')
        self.table_view.heading('3', text = 'Start')
        self.table_view.heading('4', text = 'Hours')
        self.table_view.heading('5', text = 'Notes')
        # self.table_view = GridTable(self.table_frame, num_cols = 5)
        # self.table_view.add_heading('Job', column = 1)
        # self.table_view.add_heading('Start', column = 2, columnspan = 2)
        # self.table_view.add_heading('Hours', column = 4)
        # self.table_view.add_heading('Notes', column = 5)
        self.tid_lookup = {}
        self.populate_table()

        self.edit_jobs_button = ttk.Button(self.frame, text = 'Edit Jobs', command = self.view_job_editor)
        export_options = ('Text', 'PDF')
        self.export_menu = ttk.OptionMenu(self.frame, self.export_selection, 'Export', *export_options)
        self.view_shift_button = ttk.Button(self.frame, text = 'View/Edit Shift', command = self.view_shift)

        filter_label.grid(column = 1, row = 1, sticky = W, pady = 5)
        self.search_input.grid(column = 4, row = 2, sticky = (W, E))
        self.totals_label.grid(column = 1, columnspan = 4, row = 4, sticky = W, pady = 5)
        self.table_frame.grid(column = 1, columnspan = 4, row = 5)
        self.table_view.grid(column = 1, row = 1, sticky = (N, S, E, W))
        vbar.grid(column = 2, row = 1, sticky = (N, S))
        self.export_menu.grid(column = 1, row = 6, sticky = W)
        self.edit_jobs_button.grid(column = 3, row = 6, sticky = E)
        self.view_shift_button.grid(column = 4, row = 6, sticky = E, pady = 5)

        self.frame.grid(column = 0, row = 0, padx = 5, sticky = (N, S, E, W))
        self.container.grid(column = 0, row = 0, sticky = (N, S, E, W))
        print("Grid config complete")

        self.job_menu.bind("<ButtonRelease-1>", self.filter_data)
        self.per_start_menu.bind("<ButtonRelease-1>", self.filter_data)
        self.per_end_menu.bind("<ButtonRelease-1>", self.filter_data)
        self.search_input.bind('<KeyRelease>', self.filter_data)
        self.search_input.bind("<Return>", self.filter_data)
        self.table_view.bind("<Double-Button-1>", self.view_shift)
        self.export_menu.bind("<ButtonRelease-1>", self.export)
        print("Init complete")

    def build_menu(self):
        self.choices = ['All Jobs'] + self.db.get_jobs()
        self.job_menu = ttk.OptionMenu(self.frame, self.job_selection, 'All Jobs', *self.choices)
        self.job_menu.config(width = 10)
        self.job_menu.grid(column = 1, row = 2, sticky = (W, E))
        self.job_selection.set('All Jobs')
    
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

        self.per_start_menu.grid(column = 2, row = 2, sticky = (W, E))
        self.per_end_menu.grid(column = 3, row = 2, sticky = (W, E))

    def filter_data(self, event = None):
        job_name = self.job_selection.get()
        if job_name == self.choices[0]:
            job_name = None
        period_start = self.start_selection.get()
        period_start = self.seconds_range[self.date_range.index(period_start)]
        period_end = self.end_selection.get()
        period_end = self.seconds_range[self.date_range.index(period_end)]
        search_term = self.search_input.get()
        if search_term.strip() == '': search_term = None
        self.clear_table()
        self.get_data(job_name = job_name, period_start = period_start, period_end = period_end, search_term = search_term)
        self.populate_table()
    
    def clear_table(self):
        for tid in self.tid_lookup:
            self.table_view.delete(tid)
        self.tid_lookup = {}
        # self.table_view.clear_rows()

    def get_data(self, job_name = None, period_start = None, period_end = None, search_term = None):
        self.shifts = self.db.report_shifts(job_name = job_name, period_start = period_start, period_end = period_end, search_term = search_term)
        self.total_shifts = len(self.shifts)
        self.total_hours = sum([i['hours'] for i in self.shifts])
        self.total_hours = round(self.total_hours, 2)
    
    def populate_table(self):
        self.totals_label['text'] = f'Hours: {self.total_hours}\tShifts: {self.total_shifts}'
        for shift in self.shifts[::-1]:
            if len(shift['notes']) < 20:
                notes = shift['notes']
            else:
                notes = shift['notes'][:20].split('\n')[0]
            start = shift['str_start'].split()
            values = (shift['job'], start[0], start[1], shift['hours'], notes)
            tid = self.table_view.insert('', 'end', values = values)
            self.tid_lookup[tid] = shift
    
    def view_job_editor(self):
        job_editor = EditJobs(self)
        job_editor.root.mainloop()

    def export(self, event = None):
        doc_type = self.export_selection.get()
        self.export_selection.set('Export')
        job_selection = self.job_selection.get()
        period_start = self.start_selection.get()
        period_end = self.end_selection.get()
        search_term = self.search_input.get()
        if search_term == '': search_term = None
        Export(doc_type, job_selection, period_start, period_end, search_term, self.total_hours, self.shifts)

    def view_shift(self, event = None):
        try: tid = self.table_view.focus()
        except: return
        shift = self.tid_lookup[tid]
        shift_view = ViewEditShift(self, shift)
        shift_view.root.mainloop()


class EditJobs():

    def __init__(self, ReportEdit):
        self.report_edit = ReportEdit
        
        self.root = Tk()
        self.root.title("Edit Jobs")
        self.root.resizable(False, False)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)
        self.job_selection = StringVar(self.root)

        self.table_view = ttk.Treeview(self.frame, selectmode = 'browse')
        self.table_view['columns'] = ('1', '2')
        self.table_view['show'] = 'headings'
        self.table_view.column('1', width = 100, anchor = 'w')
        self.table_view.column('2', width = 140, anchor = 'w')
        self.table_view.heading('1', text = 'Name')
        self.table_view.heading('2', text = 'Created')
        self.populate_table()

        self.edit_button = ttk.Button(self.frame, text = 'Edit Name', command = self.edit_name)

        self.table_view.grid(column = 1, columnspan = 2, row = 1, pady = (0, 5))
        self.edit_button.grid(column = 1, row = 2, sticky = W)

        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid(column = 0, row = 0)
    
    def populate_table(self):
        jobs = self.report_edit.db.get_jobs(return_dict = True)
        self.tid_lookup = {}
        for job in jobs:
            values = (job['name'], job['created'])
            tid = self.table_view.insert('', 'end', values = values)
            self.tid_lookup[tid] = job
    
    def edit_name(self):
        try: tid = self.table_view.focus()
        except: return
        job = self.tid_lookup[tid]
        entry = EntryBox(self.save_name, 'name', job['name'])
        entry.root.mainloop()
    
    def save_name(self, cur_name, new_name):
        self.report_edit.db.update_job_name()


class ViewEditShift():

    def __init__(self, ReportEdit, shift_dict):
        self.report_edit = ReportEdit
        self.shift = shift_dict

        self.root = Tk()
        self.root.title("Shift Record")
        self.root.resizable(False, False)
        # self.root.overrideredirect(True)

        self.edit_selection = StringVar(self.root)

        self.container = ttk.Frame(self.root)
        self.frame = ttk.Frame(self.container)

        self.job_label = ttk.Label(self.frame)
        self.start_label = ttk.Label(self.frame)
        self.end_label = ttk.Label(self.frame)
        self.break_label = ttk.Label(self.frame)
        self.hours_label = ttk.Label(self.frame)
        self.notes = ScrolledText(self.frame, width = 60, height = 15, relief = 'sunken')
        self.edit_frame = ttk.Frame(self.frame)
        edit_options = ('Job', 'Start', 'End', 'Break', 'Notes')
        self.edit_menu = ttk.OptionMenu(self.edit_frame, self.edit_selection, 'Edit', *edit_options)
        self.delete_button = ttk.Button(self.edit_frame, text = 'Delete Shift', command = self.delete_prompt)
        self.done_button = ttk.Button(self.frame, text = 'Done', command = self.root.destroy)
        self.load_view()

        self.job_label.grid(column = 1, row = 1, sticky = W, ipadx = 2)
        self.start_label.grid(column = 1, row = 2, sticky = W, ipadx = 5, pady = 2)
        self.end_label.grid(column = 1, row = 3, sticky = W, ipadx = 5, ipady = 0)
        self.break_label.grid(column = 2, row = 2, sticky = W, ipadx = 5, ipady = 0)
        self.hours_label.grid(column = 2, row = 3, sticky = W, ipadx = 5, ipady = 0)
        self.notes.grid(column = 1, columnspan = 2, row = 4, sticky = (N, S, E, W), pady = 5)
        self.edit_menu.grid(column = 1, row = 1, sticky = W)
        self.delete_button.grid(column = 2, row = 1, sticky = E)
        self.edit_frame.grid(column = 1, row = 5, sticky = W)
        self.done_button.grid(column = 2, row = 5, sticky = E)
        self.frame.grid(column = 0, row = 0, padx = 5, pady = 5)
        self.container.grid()

        self.root.bind("<Command-c>", self.copy_notes)
        self.edit_menu.bind("<ButtonRelease-1>", self.edit_shift)

    def load_view(self):
        self.job_label['text'] = f"Job:\t{self.shift['job']}"
        self.start_label['text'] = f"Start:\t{self.shift['str_start']}"
        self.end_label['text'] = f"End:\t{self.shift['str_end']}"
        self.break_label['text'] = f"Break:\t{self.shift['break']} (minutes)"
        self.hours_label['text'] = f"Hours:\t{self.shift['hours']}"
        self.notes.config(state = NORMAL)
        self.notes.delete('1.0', END)
        self.notes.insert(END, self.shift['notes'])
        self.notes.config(state = DISABLED)

    def edit_shift(self, event):
        key = self.edit_selection.get().lower()
        if key == 'edit': return
        elif key in ('start', 'end'):
            key = 'str_' + key
        self.edit_selection.set('Edit')
        entry = EntryBox(self.save_property, key, self.shift[key])
        entry.root.mainloop()
    
    def save_property(self, key, value):
        self.shift = self.report_edit.db.update_shift_field(self.shift['id'], key, value)
        self.load_view()
        self.report_edit.filter_data()
    
    def copy_notes(self, event = None):
        clipboard.copy(self.notes.get(1.0, END))
        print('Notes Copied')
    
    def delete_prompt(self):
        popup = PopConfirm("Permanently delete shift?", self.delete_shift)
        popup.root.mainloop()
    
    def delete_shift(self):
        self.report_edit.db.remove_shift(self.shift['id'])
        self.root.destroy()
        self.report_edit.filter_data()