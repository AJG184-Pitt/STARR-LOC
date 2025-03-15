from sgp4.api import Satrec
from sgp4.conveniences import jday
import datetime
import numpy as np

def sgp4_run(tle_line1, tle_line2, date_time: datetime.datetime):
 
    # Initiallize Satellite data
    satellite = Satrec.twoline2rv(tle_line1, tle_line2)

    # Define the date and time for propagation (Year, Month, Day, Hour, Minute, Second)
    year, month, day, hour, minute, second = date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, date_time.second
    jd, fr = jday(year, month, day, hour, minute, second)


    # Propagate the satellite position (ECI) and velocity
    e, r, v = satellite.sgp4(jd, fr,)
    
    if e != 0:
        print("Error propagating the orbit")

    # Return r = (x, y, z)
    return r

def read_tle_file(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    tle_data = []
    for i in range(0, len(lines), 3):
        if i + 2 < len(lines):
            satellite_name = lines[i].strip()
            tle_line1 = lines[i + 1].strip()
            tle_line2 = lines[i + 2].strip()
            tle_data.append((satellite_name, tle_line1, tle_line2))

    return tle_data


if __name__ == "__main__":
    pass
