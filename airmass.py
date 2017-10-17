from datetime import datetime, timedelta

J2000_UNIX_TIMESTAMP = datetime.fromtimestamp(946727930.816)

def compute_airmass(latitude, longitude, ra, dec, obs_date):
    # Useful reference: http://www.stargazing.net/kepler/altaz.html#twig02
    days_from_j2000 = \
            (obs_date - J2000_UNIX_TIMESTAMP).total_seconds() / timedelta(days=1).total_seconds()

    # This approximation is within 0.3 seconds of time for dates within 100
    # years of J2000.
    local_sidereal_time = 100.46 + 0.985647 * d + longitude + 15 * UT

def test():
    compute_airmass(None, None, None, datetime.fromtimestamp(1508268879))

if __name__ == '__main__':
    test()

