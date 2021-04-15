from os import chdir
import sys, rumps, threading
from timekeeper import db, MainApp, ShiftApp, ReportEditApp

class MenuBarApp:

    def __init__(self):
        self.app = rumps.App("Time Keeper")
        self.app.icon = "NavMenu_icon_sm.png"
        self.jobs_list = db.report_jobs()
        self.app.menu = [[rumps.MenuItem(title = "Start Shift", callback = self.start_shift),
                             [rumps.MenuItem(title = job, callback = self.start_shift) for job in self.jobs_list]],
                         rumps.MenuItem(title = "Home", callback = self.show_home),
                         rumps.MenuItem(title = "Report and Edit", callback = self.launch_report_edit)]
    
    def run(self):
        self.app.run()
    
    def run_threaded(self, func):
        thread = threading.Thread(target = func)
        thread.start()
    
    def show_home(self, event = None):
        print(event)
        app = MainApp(db)
        app.root.mainloop()
    
    @rumps.clicked(*db.report_jobs()) # does this run every time the funtion runs or just at instantiation?
    def start_shift(self, sender):
        job_name = sender.title
        print(job_name)
        app = ShiftApp(db, job_name)
        self.run_threaded(app.root.mainloop)
    
    def launch_report_edit(self, event = None):
        app = ReportEditApp(db)
        app.root.mainloop()
        pass
        

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        chdir(sys._MEIPASS)
    # menu_bar_app = MenuBarApp().run()
    app = MainApp(db)
    app.root.mainloop()