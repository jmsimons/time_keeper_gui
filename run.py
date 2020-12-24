from os import chdir
import sys
from timekeeper import app

if __name__ == "__main__":
    if getattr(sys, 'frozen', False):
        chdir(sys._MEIPASS)
    app.root.mainloop()