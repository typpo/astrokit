from datetime import datetime

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

def compute_airmass(latitude, longitude, elevation, ra, dec, obs_time):
    # http://docs.astropy.org/en/v1.1.1/coordinates/observing-example.html
    coord = SkyCoord(ra * u.deg, dec * u.deg, frame='icrs')
    loc = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=elevation)
    time = Time(obs_time.isoformat())

    altaz = coord.transform_to(AltAz(obstime=time, location=loc))
    return altaz.secz

def test():
    compute_airmass(42, -42, 0, 30, 30, datetime.fromtimestamp(1508268879))

if __name__ == '__main__':
    test()

