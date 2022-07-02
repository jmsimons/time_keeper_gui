from sys import argv
from timekeeper import db, MainApp, ShiftApp, ReportEditApp


def list_jobs():
    for job in db.report_jobs():
        print(job)

if __name__ == "__main__":
    if argv[1] == 'home':
        app = MainApp(db)
        app.root.mainloop()
    elif argv[1] == 'new_shift':
        if argv[2] in db.report_jobs():
            print(f"Starting Shift for Job: {argv[2]}")
            app = ShiftApp(db, argv[2])
            app.root.mainloop()
    elif argv[1] == 'report_edit':
        app = ReportEditApp(db)
        app.root.mainloop()
    elif argv[1] == "list_jobs":
        list_jobs()
    elif argv[1] == "add_job":
        db.add_job(argv[2])