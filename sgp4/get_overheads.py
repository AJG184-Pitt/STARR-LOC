import datetime
from satellite import Satellite
from observer import Observer
import sgp4_basic as sgpb
import pytz
from sgp4.conveniences import jday, sat_epoch_datetime
import numpy as np
import pandas as pd

import time


# load tle data
file_path = "tle.txt"
tle_data = sgpb.read_tle_file(file_path)


# create a list of satellites from the data
satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]

# Observer at the Cathedral of Learning
# (Assuming observer is at the altitude of the geodetic estimation)
observer = Observer(lat=40.44, lon=-79.96, alt=301.6)


et = pytz.timezone('US/Eastern')
local_time = datetime.datetime.now(et)
utc_time = local_time.astimezone(pytz.utc)

names = []
next_overheads = []

for sat in satellites:
    if sat.name == "IO-86" or sat.name == "QO-100":
        continue
    print(sat.name)
    names.append(sat.name)
    the_time = sat.nextOverhead(observer, utc_time)
    utc = the_time.astimezone(et)
    next_overheads.append(utc)


data = np.column_stack((names, next_overheads))

# Convert the NumPy array to a pandas DataFrame
df = pd.DataFrame(data, columns=["names", "next_overheads"])

df.to_csv("output-2.csv", index=False)
