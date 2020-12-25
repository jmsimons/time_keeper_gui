from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os, time

Base = declarative_base()


class Job(Base): # Job table definition #
    __tablename__ = 'job'
    id = Column(Integer, primary_key = True)
    name = Column(String(20), unique = True, nullable = False)
    date_created = Column(Float, nullable = False)

    def __init__(self, job_name):
        self.name = job_name
        self.date_created = time.time()
    
    def get_dict(self):
        format = '%Y/%m/%d %H:%M:%S'
        created = time.strftime(format, time.localtime(self.date_created))
        job_dict = {'id': self.id,
                    'name': self.name,
                    'created': created}
        return job_dict


class Shift(Base): # Shift table definition #
    __tablename__ = 'shift'
    id = Column(Integer, primary_key = True)
    job_name = Column(String(20), nullable = False)
    start_time = Column(Float, nullable = False)
    end_time = Column(Float, nullable = True)
    break_time = Column(Float)
    notes = Column(String(1024))
    complete = Column(Boolean)

    def __init__(self, job_name, start_time, end_time, break_time, notes, complete = False):
        self.job_name = job_name
        self.start_time = start_time
        self.end_time = end_time
        self.break_time = break_time
        self.notes = notes
        self.complete = complete
    
    def __repr__(self):
        return f'Shift(ID: {self.id}, Job: {self.job_name}, Start: {self.start_time}, End: {self.end_time}, Break: {self.break_time})'
    
    def update(self, column, value):
        # print('Updating ID:', self.id, ' Col:', column, ' Val:', value)
        format = '%Y/%m/%d %H:%M:%S'
        if column == 'job':
            self.job_name = value
        elif column in ('start', 'str_start'):
            try: value = time.mktime(time.strptime(value, format))
            except: return False
            self.start_time = value
        elif column in ('end', 'str_end'):
            try: value = time.mktime(time.strptime(value, format))
            except: return False
            self.end_time = value
        elif column == 'break':
            if value == '':
                value = 0
            self.break_time = float(value) * 60
        elif column == 'notes':
            self.notes = str(value)
        return True
    
    def get_dict(self):
        format = '%Y/%m/%d %H:%M:%S'
        str_start = time.strftime(format, time.localtime(self.start_time))
        str_end = time.strftime(format, time.localtime(self.end_time))
        if self.break_time == None: self.break_time = 0
        if self.end_time == None: self.end_time = self.start_time
        dur = self.end_time - self.start_time - self.break_time
        shift_dict = {'id': self.id,
                      'job': self.job_name,
                      'str_start': str_start,
                      'str_end': str_end,
                      'start': self.start_time,
                      'end': self.end_time,
                      'break': round(self.break_time / 60, 1),
                      'hours': round(dur / 3600, 2),
                      'notes': self.notes if self.notes != None else ''}
        return shift_dict


class DB: ### Wrapper class for database functionality ###

    def __init__(self, db_filename):
        self.engine = create_engine(f'sqlite:///{db_filename}')
        if db_filename not in os.listdir(): # Create db file if not found
            Base.metadata.create_all(bind = self.engine)
        self.Session = sessionmaker(bind = self.engine)
    
    def run_in_session(self, function, *args, **kwargs):
        s = self.Session()
        value = function(s, *args, **kwargs)
        s.commit()
        s.close()
        return value
    
    def add_job(self, job_name):
        job = Job(job_name)
        s = self.Session()
        s.add(job)
        s.commit()
        s.close()
    
    def get_jobs(self, return_dict = False):
        s = self.Session()
        if return_dict:
            jobs = [i.get_dict() for i in s.query(Job).all()]
        else:
            jobs = [i.name for i in s.query(Job).all()]
        s.close()
        return jobs
    
    def add_shift(self, job_name, start_time, end_time, break_time, notes):
        shift = Shift(job_name, start_time, end_time, break_time, notes)
        # print(shift)
        s = self.Session()
        s.add(shift)
        s.commit()
        shift_id = shift.id
        s.close()
        return shift_id
    
    def check_incomplete(self):
        s = self.Session()
        incomplete = s.query(Shift).filter(Shift.complete == False).all()
        for shift in incomplete:
            shift.complete = True
        s.commit()
        s.close()
        return len(incomplete)

    def report_shifts(self, job_name = None, period_start = None, period_end = None, search_term = None):
        # print('Filtering by job:', job_name, 'per_start:', period_start, 'per_end:', period_end, 'search_term:', search_term)
        s = self.Session()
        query = s.query(Shift).filter(Shift.complete == True)
        if job_name:
            query = query.filter(Shift.job_name == job_name)
        if search_term:
            query = query.filter(Shift.notes.ilike(f'%{search_term}%'))
        # TODO: rewrite the date filter logic with sqlalchemy methods
        shifts = query.all()
        if period_start:
            # query.filter(Shift.start_time > period_start)
            shifts = [i for i in shifts if i.start_time >= period_start]
        if period_end:
            period_end += 60 * 60 * 24 # add 24 hours
            # query.filter(Shift.end_time < period_end)
            shifts = [i for i in shifts if i.start_time < period_end]
        # shifts = [i.get_dict() for i in query.all()]
        shifts = [i.get_dict() for i in shifts]
        s.close()
        return shifts
    
    def update_job_name(self, cur_name, new_name):
        s = self.Session()
        job = s.query(Job).filter_by(name = cur_name).first()
        job.name = new_name
        s.commit()
        s.close()
    
    def update_shift(self, id, end_time, break_time, notes):
        s = self.Session()
        # print("Autosaving shift...")
        shift = s.query(Shift).filter_by(id = id).first()
        shift.end_time = end_time
        shift.break_time = break_time
        shift.notes = notes
        s.commit()
        s.close()

    def complete_shift(self, id):
        s = self.Session()
        # print("Completing shift...")
        shift = s.query(Shift).filter_by(id = id).first()
        shift.complete = True
        s.commit()
        s.close()
    
    def update_shift_field(self, id, column, value):
        s = self.Session()
        # print('Searching for', id)
        shift = s.query(Shift).filter_by(id = id).first()
        shift.update(column, value)
        shift_dict = shift.get_dict()
        s.commit()
        s.close()
        return shift_dict
    
    def remove_job(self, job_name):
        pass

    def remove_shift(self, id):
        s = self.Session()
        # print("Removing shift...")
        shift = s.query(Shift).filter_by(id = id).first()
        s.delete(shift)
        s.commit()
        s.close()
        
            