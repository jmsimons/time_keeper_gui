# time_keeper_gui
Python gui application for personal time tracking. I use this program to track time and notes on projects and contract work.

* Time Keeper is a fairly minimal gui/db application designed to track jobs, shifts, and tasks. (Runs on MacOS and Linux, hasn't been tested in Windows yet)
* It features a small home-pane that lets you add jobs, start shifts, and open the Report and Edit window.
* Shift window features tasks, notes-entry, pause_resume, and displays shift info such as job name and elappsed time. (Shift auto-updates to the database so you don't have to worry about losing your shift times or notes).
* Report and Edit displays jobs, shifts, and tasks, and allows you to open the ViewEdit pane for table item.

$python3 run.py will launch the program

*Support for tasks is currently under construction. Once finished, you will be able to mark tasks as complete from within a shift, and also view in TaskEdit window from Report and Edit. Tasks will be searchable in the Report and Edit pane.


*** Areas of growth that I invite collaboration on or that I will get to eventually ***

- Add styles to scrollbars, text, and other elements. If you're familiar with ttk Styles there are a few small tweeks that would make the UI look cleaner such as consistent bg color behind scrollbars, font-style, and an option to support dark-mode and color themes.

- Time Zone Support. Currently, all datetime information is calculated using localtime.

- Application config file and settings menu.
