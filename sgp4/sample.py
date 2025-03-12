import datetime
from satellite import Satellite
from observer import Observer
import sgp4_basic as sgpb



# load tle data
file_path = "tle.txt"
tle_data = sgpb.read_tle_file(file_path)


# create a list of satellites from the data
satellites = [Satellite(name, tle1, tle2) for name, tle1, tle2 in tle_data]

# Observer at the Cathedral of Learning
# (Assuming observer is at the altitude of the geodetic estimation)
observer = Observer(40.444067, -79.953609, 0)

r = satellites[0].getPosAtTime(datetime.datetime.now())
print(f"Current Position of satellite {satellites[0].name} is (x={r[0]}, y={r[1]}, z={r[2]}) [km].")


# Find satellite with name "AO-07"
sat = next((sat for sat in satellites if sat.name == "Taurus 1"), None)
# Check if overhead
if sat != None:
    print(f"Satellite {sat.name} is overhead = {sat.isOverhead(observer, datetime.datetime.now())}")


iss = next((sat for sat in satellites if sat.name == "ISS"), None)
if iss != None:
    print(f"Next flyover is: {sat.nextOverhead(observer, datetime.datetime.now())}")




