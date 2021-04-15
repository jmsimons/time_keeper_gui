
import os
from timekeeper.Main import MainApp, ShiftApp
from timekeeper.ReportEdit import ReportEditApp
from timekeeper.Database import DB

db_filename = 'time.db'
db = DB(db_filename)

# app = MainApp(db)