from datetime import datetime

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

def compute_airmass_from_analysis(analysis, ra, dec):
    return compute_airmass(analysis.image_latitude, analysis.image_longitude,
            analysis.image_elevation, analysis.image_datetime, ra, dec)

def compute_airmass(latitude, longitude, elevation, obs_time, ra, dec):
    # Astropy reference: http://docs.astropy.org/en/v1.1.1/coordinates/observing-example.html
    # For the math behind it: http://www.stargazing.net/kepler/altaz.html#twig02
    coord = SkyCoord(ra * u.deg, dec * u.deg, frame='icrs')
    loc = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=elevation)
    time = Time(obs_time.strftime('%Y-%m-%d %H:%M:%SZ'), format='iso')

    altaz = coord.transform_to(AltAz(obstime=time, location=loc))
    return altaz.secz

def test():
    compute_airmass(42, -42, 0, datetime.fromtimestamp(1508268879), 30, 30)

if __name__ == '__main__':
    test()

