#!/usr/bin/env python

import math

from astropy.io import fits
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
# from astropy.coordinates import Angle

# https://groups.google.com/forum/#!topic/astrometry/Lk1LuhwBBNU
im = fits.open('/home/ian/Downloads/corrtest.fits')
data = im[1].data
radec_pairs = zip(data['index_ra'], data['index_dec'], data['FLUX'])

simbad = Simbad()
# http://astroquery.readthedocs.io/en/latest/simbad/simbad.html
# http://simbad.u-strasbg.fr/simbad/sim-help?Page=sim-fscript#VotableFields
# http://simbad.u-strasbg.fr/simbad/sim-id?protocol=html&Ident=Wolf%201061&output.format=VOTable
simbad.add_votable_fields('fluxdata(V)', 'flux_unit(mag)', 'flux_system(mag)')
comparison_objs = []
for ra, dec, flux in radec_pairs[:10]:
    print 'ra, dec, flux:', ra, dec, flux
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
    # print desig, r2mag

    comparison_objs.append({
        'designation': desig,
        'reference_Rmag': r2mag,

        # TODO(ian): Use astrokit psf flux.
        'observed_flux': flux,
    })

print comparison_objs

for i in range(len(comparison_objs)):
    print '*' * 80
    comparisons = comparison_objs[:]
    target = comparisons[i]
    del comparisons[i]

    diff_sum = 0
    mag_targets = []
    for comparison in comparisons:
        # TODO(ian): Really should be ADU/Exposure
        instrumental_mag_target = -2.5 * math.log10(target['observed_flux'])
        instrumental_mag_comparison = -2.5 * math.log10(comparison['observed_flux'])

        # Very basic standard magnitude formula from Brian Warner.
        mag_target = (instrumental_mag_target - instrumental_mag_comparison) + comparison['reference_Rmag']
        mag_targets.append(mag_target)
        print 'computed', mag_target, 'vs actual', target['reference_Rmag']

        diff_sum += instrumental_mag_target - instrumental_mag_comparison

    # Compute differential magnitude.
    target_diff_magnitude = diff_sum / len(comparisons)
    print 'target diff magnitude:', target_diff_magnitude

    target_mag_avg = sum(mag_targets) / len(comparisons)
    print 'mag target average:', target_mag_avg, 'vs actual', target['reference_Rmag']
    percent_error = (target['reference_Rmag'] - target_mag_avg) / target['reference_Rmag'] * 100.0
    print '  --> difference:', (target_mag_avg - target['reference_Rmag'])
    print '  --> % error:', percent_error
