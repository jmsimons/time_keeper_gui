import sys
from date_time_handler import DateTimeHandler
from timekeeper import db
from timekeeper.export import Export

dt = DateTimeHandler()

job_name = sys.argv[1]
period_start = sys.argv[2]
period_end = sys.argv[3]
period_start_ts = dt.timestamp(sys.argv[2])
period_end_ts = dt.timestamp(sys.argv[3])

print(f"Fetching shifts for {job_name}, {period_start}_{period_start_ts}, {period_end}_{period_end_ts}")
shifts = db.report_shifts(job_name = job_name, period_start = period_start_ts, period_end = period_end_ts)
for shift in shifts:
    shift["tasks"] = db.report_tasks(shift_id = shift["id"])
total_hours = sum([i['hours'] for i in shifts])
total_hours = round(total_hours, 2)


Export('Text', job_name, period_start, period_end, None, total_hours, shifts)