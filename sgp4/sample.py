import datetime
from satellite import Satellite
from observer import Observer
import sgp4_basic as sgpb
import pytz
from sgp4.conveniences import jday, sat_epoch_datetime

import time


# load tle data
file_path = "tle.txt"
tle_data = sgpb.read_tle_file(file_path)


# create a list of satellites from the data
satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]

# Observer at the Cathedral of Learning
# (Assuming observer is at the altitude of the geodetic estimation)
observer = Observer(lat=40.444, lon=-79.953, alt=300)


et = pytz.timezone('US/Eastern')
local_time = datetime.datetime.now(et)
utc_time = local_time.astimezone(pytz.utc)


r = satellites[0].getPosAtTime(utc_time)
print(f"Current Position of satellite {satellites[0].name} is (x={r[0]}, y={r[1]}, z={r[2]}) [km].")

vec = satellites[0].getAngleFrom(observer, utc_time)
print(f"Current angle from observer to satellite {satellites[0].name} is (Azimuth={vec[0]}, Elevation={vec[1]}, Distance={vec[2]}) [degrees, degrees, meters].")


# Find satellite with name "AO-07"
sat = next((sat for sat in satellites if sat.name == "ISS"), None)
# Check if overhead
if sat != None:
    #print(f"Satellite {sat.name} is overhead = {sat.isOverhead(observer, utc_time)}")
    pass


iss = next((sat for sat in satellites if sat.name == "ISS"), None)
if iss != None:
    overhead = iss.nextOverhead(observer, utc_time)
    start = time.time()
    print(f"Next flyover of the ISS is: {overhead.astimezone(et)}")
    print(f"Next overhead duration of the ISS : {iss.overheadDuration(observer, utc_time)}")
    end = time.time()

else:
    print("NONE")


#print("The time of execution of above program is:", (end-start) * 10**3, "ms")



start = time.time()

iss.isOverhead(observer, utc_time)
iss.getAngleFrom(observer, utc_time)

end = time.time()

#print("The time of execution isOverhead is:", (end-start) * 10**3, "ms")


