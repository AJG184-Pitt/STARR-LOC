import tkinter as tk
from tkinter import ttk

import sys
sys.path.append('../sgp4')

import sgp4_basic as sgpb
from observer import Observer
from satellite import Satellite
import pytz, datetime

def main():
    # Information gathering
    file_path = "../sgp4/tle.txt"
    tle_data = sgpb.read_tle_file(file_path)
    satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]

    observer = Observer(40.44, -79.95, 300)

    et = pytz.timezone("US/Eastern")
    local_time = datetime.datetime.now(et)
    utc_time = local_time.astimezone(pytz.utc)

    # Create the main windows
    root = tk.Tk()

    # Set size constraints
    root.minsize(1280, 720)
    root.maxsize(1280, 720)

    # Labels for text display
    # options = ['SAT1', 'SAT2', 'SAT3']
    options = [sat.name for sat in satellites]
    combo_box = ttk.Combobox(root, values=options, width=50)

    e1 = tk.Entry(root, bg='yellow', width=50)
    e2 = tk.Entry(root, bg='red', width=50)
    e3 = tk.Entry(root, bg='green', width=50)

    empty1 = tk.Label(root, bg='#f0f0f0', width=50, height=5)
    empty2 = tk.Label(root, bg='#f0f0f0', width=50, height=5)
    empty3 = tk.Label(root, bg='#f0f0f0', width=50, height=5)

    # Add text to entry frames
    e1.insert(0, "Dummy Text 1")
    e2.insert(0, "Dummy Text 2")
    e3.insert(0, "Dummy Text 3")

    # Sets grid positions for empty frames
    empty1.grid(row=1, column=0)
    empty2.grid(row=2, column=0)
    empty3.grid(row=3, column=1)

    # Sets grid positions for frames
    combo_box.grid(row=6, column=0)
    e1.grid(row=5, column=2, pady=10)
    e2.grid(row=6, column=2, pady=10)
    e3.grid(row=7, column=2, pady=10)

    # Start gui with event loop
    root.mainloop()


    def get_sat_data(self):
        return

if __name__ == '__main__':
    # satellite = Satellite("SAT1", )
    main()
