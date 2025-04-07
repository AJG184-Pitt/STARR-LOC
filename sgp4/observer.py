from pymap3d import geodetic2eci

class Observer:
    def __init__(self, **kwargs):
        """Pass in either file_path to GPS coordinates, or lat=, lon=, alt= directly"""

        file_path = kwargs.get('file_path', None)

        if file_path == None:
            self.lat = kwargs.get('lat', None)
            self.lon = kwargs.get('lon', None)
            self.alt = kwargs.get('alt', None)
        else:
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            for line in lines:
                x = line.split(" ")
                self.lat = float(x[0])
                self.lon = float(x[1])
                self.alt = float(x[2])
                break

    def getEciPos(self, date_time):
        """
        Calculate ECI coordinates of the observer at a given time
        """
        return geodetic2eci(self.lat, self.lon, self.alt, date_time, deg=True)
    
    
