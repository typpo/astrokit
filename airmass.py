from datetime import datetime

from astropy import units as u
from astropy.time import Time
from astropy.coordinates import SkyCoord, EarthLocation, AltAz

def annotate_with_airmass(analysis, reduction):
    annotated_stars = []
    for star in analysis.catalog_reference_stars:
        ra = star['index_ra']
        dec = star['index_dec']
        computed_airmass = compute_airmass_for_point(analysis.image_latitude,
                analysis.image_longitude, analysis.image_elevation,
                analysis.image_datetime, ra, dec)
        star['airmass'] = float(computed_airmass)

        annotated_stars.append(star)
    return annotated_stars

def compute_airmass_for_point(latitude, longitude, elevation, obs_time, ra, dec):
    # Astropy reference: http://docs.astropy.org/en/v1.1.1/coordinates/observing-example.html
    # For the math behind it: http://www.stargazing.net/kepler/altaz.html#twig02
    coord = SkyCoord(ra * u.deg, dec * u.deg, frame='icrs')
    loc = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=elevation)
    time = Time(obs_time.strftime('%Y-%m-%d %H:%M:%SZ'), format='iso')

    altaz = coord.transform_to(AltAz(obstime=time, location=loc))
    return altaz.secz

def test():
    compute_airmass_for_point(42, -42, 0, datetime.fromtimestamp(1508268879), 30, 30)

if __name__ == '__main__':
    test()

