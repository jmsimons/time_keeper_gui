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
    # complete = Column(Boolean)

    def __init__(self, job_name, start_time, end_time, break_time, notes, complete = False):
        self.job_name = job_name
        self.start_time = start_time
        self.end_time = end_time
        self.break_time = break_time
        self.notes = notes
        # self.complete = complete
    
    def __repr__(self):
        return f'Shift(Job: {self.job_name}, Start: {self.start_time}, End: {self.end_time}, Break: {self.break_time})'
    
    def update(self, column, value):
        print('Updating ID:', self.id, ' Col:', column, ' Val:', value)
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
            self.break_time = float(value) * 60
        elif column == 'notes':
            self.notes = str(value)
        return True
    
    def get_dict(self):
        format = '%Y/%m/%d %H:%M:%S'
        str_start = time.strftime(format, time.localtime(self.start_time))
        str_end = time.strftime(format, time.localtime(self.end_time))
        dur = self.end_time - self.start_time - self.break_time
        shift_dict = {'id': self.id,
                      'job': self.job_name,
                      'str_start': str_start,
                      'str_end': str_end,
                      'start': self.start_time,
                      'end': self.end_time,
                      'break': round(self.break_time / 60, 1),
                      'hours': round(dur / 3600, 2),
                      'notes': self.notes}
        return shift_dict