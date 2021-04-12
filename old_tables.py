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
    # TODO: Add notes

    def __init__(self, job_name):
        self.name = job_name
        self.date_created = time.time()
    
    def update(self, column, value):
        if column == 'name':
            self.name = value
        return True
    
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
    # TODO: Change job_name to job_id
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


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key = True)
    shift_id = Column(Integer, nullable = False)
    # TODO: remove job name
    job_name = Column(String(20), nullable = False)
    title = Column(String(20), nullable = False)
    time_created = Column(Float, nullable = False)
    notes = Column(String(1024))
    # TODO: convert complete to time_complete, nullable = True
    complete = Column(Boolean)

    def __init__(self, job_name, shift_id, title, notes = None):
        self.shift_id = shift_id
        self.job_name = job_name
        self.title = title
        self.time_created = time.time()
        self.notes = notes if notes else ""
        self.complete = False
    
    def __repr__(self):
        return f'Task(ID: {self.id}, Shift_ID: {self.shift_id}, Job: {self.job_name},  Title: {self.title}, Created: {self.time_created}, Notes_len: {len(self.notes)}, Complete: {self.complete})'

    def update(self, column, value):
        if column == 'title':
            self.title = value
        elif column == 'complete':
            self.complete = bool(value)
        elif column == 'notes':
            self.notes = str(value)
        return True

    def get_dict(self):
        format = '%Y/%m/%d %H:%M:%S'
        time_created = time.strftime(format, time.localtime(self.time_created))
        # TODO: query for job_name
        task_dict = {'id': self.id,
                     'job_name': self.job_name,
                     'title': self.title,
                     'time_created': time_created,
                     'complete': self.complete,
                     'notes': self.notes if self.notes != None else ''}
        return task_dict