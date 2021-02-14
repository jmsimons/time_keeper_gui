from tkinter import ttk, Label, Canvas, Text, StringVar, INSERT, END, N, S, E, W, NORMAL, DISABLED

class GridTable(ttk.Frame):

    def __init__(self, parent, num_cols = 1, open_func = None, selectmode = None):
        # Select modes: 
        self.num_cols = num_cols
        self.open_func = open_func
        self.size = (300, 200)
        self.row_pad = 0
        self.col_pad = 5
        self.headings = []
        self.rows = []
        ttk.Frame.__init__(self, parent, width = 300, height = 300)
        self.canvas = Canvas(self, width = 350, height = 300)
        self.grid_frame = ttk.Frame(self.canvas, relief = "sunken")
        vbar = ttk.Scrollbar(self, orient = 'vertical', command = self.canvas.yview)
        self.canvas.config(yscrollcommand = vbar.set)

        vbar.grid(row = 1, column = 2, sticky = (N, S))
        self.grid_frame.grid(row = 1, column = 1, padx = (1, 0), pady = (1, 0), sticky = (N, S, E, W))
        self.canvas.grid(row = 0, column = 0, sticky = (N, S, E, W))
        self.grid_propagate(False)

        # self.table_frame.create_window((0, 0), window = self.grid_frame, anchor='nw')
        self.grid(padx = (1, 0), pady = (1, 0))
        self.grid_propagate(False)

    def easy_headings(self, *headings):
        if self.headings:
            self.clear_headings()
        for i in range(self.num_cols):
            heading = ttk.Label(self.grid_frame, text = headings[i])
            heading.grid(row = 1, column = (i + 1), padx = (0, 1), pady = (0, 2), sticky = (E, W))
            self.headings.append(heading)

    def add_heading(self, text, **kwargs):
        # print("Adding heading:", text)
        label_kwargs = {}
        grid_kwargs = {'row': 1, 'padx': (0, 2), 'pady': (0, 4), 'sticky': (E, W)}
        if 'width' in kwargs: label_kwargs.update(kwargs.pop('width'))
        grid_kwargs.update(kwargs)
        heading = ttk.Label(self.grid_frame, text = text, **label_kwargs)
        heading.grid(**grid_kwargs)

    def insert_row(self, *values):
        row_num = len(self.rows) + 2
        print("Inserting row", row_num, end = '')
        row = []
        for i in range(self.num_cols):
            print(" column", i + 1, end = '')
            item = Label(self.grid_frame, text = values[i])
            # item = Text(self.grid_frame)
            # item.insert(INSERT, values[i])
            # item.config(state = DISABLED)
            item.grid(row = row_num, column = i + 1, sticky = (E, W))
            # item.bind("<Button-1>", self.return_row)
            # item.bind("<Double-Button-1>", self.return_row)
            row.append(item)
        print()
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