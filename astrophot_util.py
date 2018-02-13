from cStringIO import StringIO

from astropy.io import fits

def get_fits_from_raw(data):
    return fits.open(StringIO(data))

