
import os
from timekeeper.Main import MainApp
from timekeeper.Database import DB

db_filename = 'time.db'
db = DB(db_filename)

app = MainApp(db)