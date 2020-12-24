from Database import Job, Shift, DB
from old_tables import Shift as oldShift

old_db = DB("old_time.db")
new_db = DB("time.db")

old_s = old_db.Session()
new_s = new_db.Session()

jobs = old_s.query(Job).all()
for job in jobs:
    new_job = Job(job.name)
    new_job.date_created = job.date_created
    new_s.add(new_job)
new_s.commit()

shifts = old_s.query(oldShift).all()
for shift in shifts:
    new_shift = Shift(shift.job_name, shift.start_time, shift.end_time, shift.break_time, shift.notes, complete = True)
    new_s.add(new_shift)
new_s.commit()

old_s.close()
new_s.close()