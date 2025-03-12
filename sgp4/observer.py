from pymap3d import geodetic2eci

class Observer:
    def __init__(self, lat, lon, alt):
        self.lat = lat
        self.lon = lon
        self.alt = alt

    def getEciPos(self, date_time):
        """
        Calculate ECI coordinates of the observer at a given time
        """
        return geodetic2eci(self.lat, self.lon, self.alt, date_time, deg=True)
        