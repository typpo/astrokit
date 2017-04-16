#!/usr/bin/env python

from astropy.io import fits
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
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
    print 'ra, dec:', ra, dec
    '''
    result = simbad.query_region('%f %f' % (ra, dec))
    if result:
        print result['MAIN_ID'].data, result['FLUX_V'].data
    '''

    # Query USNO catalog.
    v = Vizier(columns=['_RAJ2000', '_DEJ2000','B-V', 'R2mag', 'B2mag', 'USNO-B1.0'])
    results = v.query_region('%f %f' % (ra, dec), radius='1s', catalog='I/284/out')
    if len(results) < 1:
        continue
    r2mag = results[0]['R2mag'].data[0]
    desig = results[0]['USNO-B1.0'].data[0]
    print desig, r2mag
