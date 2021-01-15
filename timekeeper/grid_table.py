from tkinter import ttk, Canvas, Text, StringVar, INSERT, END, N, S, E, W, NORMAL, DISABLED

class GridTable(ttk.Frame):

    def __init__(self, parent, num_cols = 1, open_func = None, selectmode = None):
        # Select modes: 
        self.num_cols = num_cols
        self.open_func = open_func
        self.headings = []
        self.rows = []
        ttk.Frame.__init__(self, parent, relief = "sunken")
        self.table_frame = Canvas(self)
        self.table_frame.config(width = 450, height = 400)
        vbar = ttk.Scrollbar(self, orient = 'vertical', command = self.table_frame.yview)
        self.table_frame.config(yscrollcommand = vbar.set)

        vbar.grid(row = 1)
        self.table_frame.grid(row = 0, column = 0, padx = (1, 0), pady = (1, 0), sticky = (N, S, E, W))
        self.grid(row = 0, column = 0, sticky = (N, S, E, W))

    def easy_headings(self, *headings):
        if self.headings:
            self.clear_headings()
        for i in range(self.num_cols):
            heading = ttk.Label(self.table_frame, text = headings[i])
            heading.grid(row = 1, column = (i + 1), padx = (0, 1), pady = (0, 2), sticky = W)
            self.headings.append(heading)

    def add_heading(self, text, **kwargs):
        # print("Adding heading:", text)
        heading = ttk.Label(self.table_frame, text = text, )
        heading.grid(row = 1, padx = (0, 1), pady = (0, 2), sticky = W)
        heading.grid(**kwargs)

    def insert_row(self, *values):
        # print("Inserting row:", *values)
        row_num = len(self.rows) + 2
        row = []
        for i in range(self.num_cols):
            item = Text(self.table_frame, state = DISABLED)
            item.insert(INSERT, values[i])
            # item.config()
            item.grid(row = row_num, column = i + 1)
            # item.bind("<Button-1>", self.return_row)
            # item.bind("<Double-Button-1>", self.return_row)
            row.append(item)
        self.rows.append(row)
        return row_num
    
    def select_row(self, event = None):
        print(event)
        row_num = event.widget.grid_location()[1]
        # TODO: highlight row
    
    def return_row(self, event = None):
        print(event)
        return event.widget.grid_location()[1]

    def clear_headings(self):
        for heading in self.headings:
            heading.destroy()
        self.headings = []

    def clear_rows(self):
        for row in self.rows:
            for item in row:
                item.destroy()
        self.rows = []