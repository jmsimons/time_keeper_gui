
from textwrap import TextWrapper
from reportlab.pdfgen.canvas import Canvas
import os

class Export():

    def __init__(self, doc_type, job_selection, period_start, period_end, search_term, total_hours, shifts):
        self.job_selection = job_selection
        self.period_start = period_start
        self.period_end = period_end
        self.search_term = search_term
        period_start = '-'.join(period_start.split('/'))
        period_end = '-'.join(period_end.split('/'))
        self.filename = f'{job_selection}_{period_start}_{period_end}'
        if search_term: self.filename += f'_({self.search_term})'
        self.total_hours = total_hours
        self.shifts = shifts
        self.compile()
        if doc_type == 'Text': self.write_txt()
        elif doc_type == 'PDF': self.write_pdf()
        # os.startfile(self.filename)

    def compile(self):
        # TODO: Preserve white space in notes
        wrapper = TextWrapper(initial_indent = '\t', subsequent_indent = '\t', fix_sentence_endings = True, replace_whitespace = True)
        output = [f'Shift Report for Period: {self.period_start} - {self.period_end}\n']
        output.append(f'Job: {self.job_selection}\t\tSearch Term: {self.search_term}\n')
        output.append(f'Period Hours: {self.total_hours}\tPeriod Shifts: {len(self.shifts)}\n\n')
        output.append('* Shifts *')
        for shift in self.shifts:
            output.append(f"\n{shift['job']}\t\t{shift['str_start']}\t\t{shift['hours']}\t\tNotes:")
            output.extend(wrapper.wrap(shift['notes']))
        output.append('\n* End of Report *')
        self.output = output
    
    def write_txt(self):
        self.filename = f'export/{self.filename}.txt'
        output = '\n'.join(self.output)
        with open(self.filename, 'w') as f:
            f.write(output)
    
    def write_pdf(self):
        self.filename += '.pdf'
        canvas = Canvas(self.filename, pagesize = (612, 792))
        canvas.drawString(1*72, 10*72, self.output)
        canvas.save()