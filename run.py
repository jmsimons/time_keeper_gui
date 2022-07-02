from os import chdir, system
import sys, rumps, threading, subprocess
import multiprocessing as mp
from timekeeper import db, MainApp, ShiftApp, ReportEditApp


class MenuBarApp:

    '''
    - This class contains entities and methods for the MacOS menu bar icon application
    - From the menu bar application, the user can open the home pane, start a new shift, or open the report/edit feature
    '''

    def __init__(self):
        self.app = rumps.App("Time Keeper")
        self.app.icon = "NavMenu_icon_sm.png"
        self.jobs_list = db.report_jobs()
        shift_submenu = [rumps.MenuItem(i, callback = self.start_shift) for i in self.jobs_list]
        self.app.menu = [[rumps.MenuItem(title = "Start Shift"), shift_submenu],
                         rumps.MenuItem(title = "Home", callback = self.show_home),
                         rumps.MenuItem(title = "Report and Edit", callback = self.launch_report_edit)]
    
    def run(self):
        self.app.run()
    
    def show_home(self, event = None):
        system(f"python time_keeper_cli.py home &")
    
    @rumps.clicked(*db.report_jobs())
    def start_shift(self, sender):
        job = "\ ".join(sender.title.split(' '))
        response = system(f"python time_keeper_cli.py new_shift {job} &")
        print(response)

    def launch_report_edit(self, event = None):
        system(f"python time_keeper_cli.py report_edit &")
        

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        chdir(sys._MEIPASS)
    # for MacOS menu bar icon
    menu_bar_app = MenuBarApp().run()

    # # for Linux
    # app = MainApp(db)
    # app.root.mainloop()