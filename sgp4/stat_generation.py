import matplotlib.pyplot as plt
import numpy as np

import datetime
from satellite import Satellite
from observer import Observer
import sgp4_basic as sgpb
import pytz
from sgp4.conveniences import jday, sat_epoch_datetime

import time


file_path = "tle.txt"
tle_data = sgpb.read_tle_file(file_path)

satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]
observer = Observer(lat=40.444, lon=-79.953, alt=300)


et = pytz.timezone('US/Eastern')
local_time = datetime.datetime.now(et)
utc_time = local_time.astimezone(pytz.utc)

names = []
next_overhead = []
overhead_duration = []


angles = []

sat = next((sat for sat in satellites if sat.name == "ISS"), None)

next_overhead = sat.nextOverhead(observer, utc_time)
date_time = next_overhead
while (sat.isOverhead(observer, date_time)):
    angles.append(sat.getAngleFrom(observer, date_time))
    date_time += datetime.timedelta(seconds=1)

az_list = []
el_list = []

for angle in angles:
    az_list.append(angle[0])
    el_list.append(angle[1])
    print(f"Angle = {angle}, time = {date_time}")

# Sample data
azimuths = np.array(az_list)
elevations = np.array(el_list)  # Elevation from 0 (edge) to 90 (center)

# Convert elevation to "inverted radius" so 0° is at the edge and 90° is at the center
radii = 1 - elevations / 90.0
azimuths_rad = np.deg2rad(azimuths)

# Create polar plot
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_theta_zero_location("N")
ax.set_theta_direction(1)

# Plot points
ax.scatter(azimuths_rad, radii, c='red')

# Custom radial ticks and labels
elevation_degrees = np.arange(0, 91, 15)  # 0°, 15°, ..., 90°
radii_ticks = 1 - elevation_degrees / 90.0  # Map to inverted radii
ax.set_yticks(radii_ticks)
ax.set_yticklabels([f"{deg}°" for deg in elevation_degrees])

# Remove the auto radial limit and enforce ours
ax.set_ylim(0, 1)

ax.set_title("Next ISS Pass")
plt.savefig("iss_pass.png", dpi=300, bbox_inches='tight', transparent=True)
plt.show()