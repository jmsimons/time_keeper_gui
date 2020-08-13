import sys, pickle, json

sys.path.insert(0, '/Users/jaredsimons/Desktop/Projects/time_keeper')

from timekeeper import db

with open('/Users/jaredsimons/Desktop/Projects/time_keeper/jobs.pkl', 'rb') as bf:
    jobs = pickle.load(bf)

convert = {'keeper': 'TimeKeeper', 'villopoto': 'Villopoto', 'vscope': 'VScope'}

job_names = [i for i in jobs.keys() if i != 'job']
shifts = []

# Add jobs to db and shifts to list #
for job in job_names:
    db.add_job(convert[job])
    for shift in jobs[job]:
        shift = list(shift)
        shift.append(convert[job])
        shifts.append(shift)

# Sort shifts by start_time
def item_zero(i):
    return i[0]

shifts.sort(key = item_zero)

# Add shifts to db
for shift in shifts:
    db.add_shift(shift[3], shift[0], shift[1], 0, shift[2])
