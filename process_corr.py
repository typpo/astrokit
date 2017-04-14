#!/usr/bin/env python

from astropy.io import fits
from astroquery.simbad import Simbad
# from astropy.coordinates import Angle

# https://groups.google.com/forum/#!topic/astrometry/Lk1LuhwBBNU
im = fits.open('/home/ian/Downloads/corrtest.fits')
data = im[1].data
radec_pairs = zip(data['index_ra'], data['index_dec'])

simbad = Simbad()
# http://astroquery.readthedocs.io/en/latest/simbad/simbad.html
# http://simbad.u-strasbg.fr/simbad/sim-help?Page=sim-fscript#VotableFields
# http://simbad.u-strasbg.fr/simbad/sim-id?protocol=html&Ident=Wolf%201061&output.format=VOTable
simbad.add_votable_fields('fluxdata(V)', 'flux_unit(mag)', 'flux_system(mag)')
print len(radec_pairs)
for ra, dec in radec_pairs[:30]:
    print ra, dec
    result = simbad.query_region('%f %f' % (ra, dec))
    if result:
        print result['MAIN_ID'].data, result['FLUX_V'].data

# v = Vizier(columns=['_RAJ2000', '_DEJ2000','B-V', 'Vmag', 'Plx'])
# v.query_region('7.4527083453 -33.3246888886', radius='1s')

