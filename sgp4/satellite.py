import datetime
import numpy as np

from pymap3d import eci2aer

import sgp4_basic as sgpb
from observer import Observer

class Satellite:
    def __init__(self, satellite_name: str, tle_line1: str, tle_line2: str):
        self.name = satellite_name
        self.tle1 = tle_line1
        self.tle2 = tle_line2

    def getPosAtTime(self, date_time: datetime.datetime):
        """
        Get the ECI coordinates of the satellite. Returns Tuple (x, y, z) in km
        """

        return sgpb.sgp4_run(self.tle1, self.tle2, date_time)

    def getAngleTo(self, observer: Observer, date_time):
        """
        Returns Tuple (Azimuth, Elevation, Dist)
        """
    
        r = self.getPosAtTime(date_time)
        return eci2aer(r[0], r[1], r[2], observer.lat, observer.lon, observer.alt, date_time, deg=True)
        

    def isOverhead(self, observer, date_time):
        """
        Check if the satellite is overhead
        """

        return self.getAngleTo(observer, date_time)[1] > 40

    def nextOverhead(self, observer, date_time):
        """
        Returns the datetime when the satellite will be overhead next
        """

        while (not self.isOverhead(observer, date_time)):
            date_time = date_time + datetime.timedelta(seconds=60)
            print(f"trying time: {date_time}")

        return date_time
        

    def overheadDuration(self, observer, date_time, **kwargs):
        """
        Returns the time that the satellite will remain overhead, or the duration of the next overhead.
        Returns tuple (minutes, seconds)
        Optional param 'next_overhead' - use if you have already calculated next_overhead to save time
        """

        next_overhead = kwargs.get('next_overhead', None)

        if not self.isOverhead(observer, date_time):
            if next_overhead != None:
                date_time = next_overhead
            else:
                date_time = self.nextOverhead(observer, date_time)

        orig_time = date_time
        while (self.isOverhead(observer, date_time)):
            date_time += datetime.timedelta(seconds=1)

        time_diff = date_time - orig_time
        time = divmod(time_diff.total_seconds(), 60)
        minutes, seconds = time[0], time[1]

        return (minutes, seconds)
               


if __name__ == "__main__":
    pass