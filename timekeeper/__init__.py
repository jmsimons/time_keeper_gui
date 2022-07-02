
import os
from timekeeper.main import Tk, MainApp, ShiftApp
from timekeeper.report_edit import ReportEditApp
from timekeeper.database import DB

db_filename = 'time.db'
db = DB(db_filename)

# app = MainApp(db)