#!/usr/bin/env python

import argparse
import json
import math
import os
import shelve

import numpy as np

from astropy.io import fits
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from rtree import index as rTreeIndex

cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache/catalog.db')
cache = shelve.open(cache_path)

vizier = Vizier(columns=['_RAJ2000', '_DEJ2000','B-V', 'R2mag', 'B2mag', 'USNO-B1.0'])

def vizier_lookup(ra, dec):
    searchstr = '%f %f' % (ra, dec)
    results = cache.get(searchstr)
    if not results:
        results = vizier.query_region(searchstr, radius='1s', catalog='I/284/out')
        if len(results) > 0:
            cache[searchstr] = results
    return results

def choose_reference_stars(corr_fits_path, point_source_json_path):
    '''
    Joins stars found in point source extraction/flux computation step with
    stars from the astrometry step with known J2000 ra, dec.
    '''

    # First, extracted point sources.
    pse_points = json.load(open(point_source_json_path, 'r'))

    # Then corr file.
    # corr.fits from astrometry.net.  See https://groups.google.com/forum/#!topic/astrometry/Lk1LuhwBBNU
    im = fits.open(corr_fits_path)
    data = im[1].data

    # And build a lookup tree out of it.
    tree = rTreeIndex.Index()
    for count, row in np.ndenumerate(data):
        rowdata = dict(zip(data.names, row))
        coords = (rowdata['field_x'], rowdata['field_y'])
        tree.insert(count, coords, obj=rowdata)

    # Now, for each extracted point source, try to find its (ra, dec). If so,
    # include it as a possible reference star.
    for point in pse_points:
        coord_x = point['field_x']
        coord_y = point['field_y']
        mag_instrumental = point['est_mag']

def main():
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
    for ra, dec, flux in radec_pairs:
        print 'ra, dec, flux:', ra, dec, flux
        '''
        result = simbad.query_region('%f %f' % (ra, dec))
        if result:
            print result['MAIN_ID'].data, result['FLUX_V'].data
        '''

        # Query USNO catalog.
        results = vizier_lookup(ra, dec)
        if len(results) < 1:
            continue
        r2mag = float(results[0]['R2mag'].data[0])
        if math.isnan(r2mag):
            print '  --> skipping due to no r2mag'
            continue
        desig = results[0]['USNO-B1.0'].data[0]
        # print desig, r2mag

        comparison_objs.append({
            'designation': desig,
            'reference_Rmag': r2mag,

            # TODO(ian): Use astrokit psf flux.
            'observed_flux': flux,
        })

    print comparison_objs

    percent_errors = []
    for i in range(len(comparison_objs)):
        print '*' * 80
        comparisons = comparison_objs[:]
        target = comparisons[i]
        del comparisons[i]

        comparison_diffs = 0
        target_mags = []
        for comparison in comparisons:
            # TODO(ian): Really should be ADU/Exposure
            instrumental_target_mag = -2.5 * math.log10(target['observed_flux'])
            instrumental_mag_comparison = -2.5 * math.log10(comparison['observed_flux'])

            # Compute basic standard magnitude formula from Brian Warner.
            target_mag = (instrumental_target_mag - instrumental_mag_comparison) + comparison['reference_Rmag']
            target_mags.append(target_mag)
            # print 'computed', target_mag, 'vs actual', target['reference_Rmag']

            comparison_diffs += instrumental_target_mag - instrumental_mag_comparison

        # Compute differential magnitude.
        comparison_mean = np.mean(comparison_diffs)
        comparison_std = np.std(comparison_diffs)
        print 'comparison magnitude diff average:', comparison_mean
        print 'comparison magnitude diff std:', comparison_std

        target_mag_avg = np.mean(target_mags)
        target_mag_std = np.std(target_mags)
        print 'mag target average:', target_mag_avg, 'vs actual', target['reference_Rmag']
        print 'mag target std:', target_mag_std

        percent_error = abs(target['reference_Rmag'] - target_mag_avg) / target['reference_Rmag'] * 100.0
        percent_errors.append(percent_error)
        print '  --> difference:', (target_mag_avg - target['reference_Rmag'])
        print '  --> % error:', percent_error

    print '=' * 80
    print 'percent error avg (MAPE):', np.mean(percent_errors)
    print 'percent error max:', max(percent_errors)
    print 'percent error min:', min(percent_errors)

def get_args():
    parser = argparse.ArgumentParser('Extract point sources from image.')
    parser.add_argument('--corr_fits',
                        help='fits astrometry output with J2000 ra and dec.',
                        required=True)
    parser.add_argument('--point_source_json',
                        help='point source json output, annotated with flux and instrumental magnitude',
                        required=True)
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    choose_reference_stars(args.corr_fits, args.point_source_json)
    #main()
