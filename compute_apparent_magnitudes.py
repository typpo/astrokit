#!/usr/bin/env python

import argparse
import json
import logging
import math
import os
import shelve

from cStringIO import StringIO

import numpy as np

from astropy.io import fits
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from rtree import index as rTreeIndex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache/catalog.db')
cache = shelve.open(cache_path)

# Maximum distance, in pixels, to accept a match for an object between our
# point source extraction and astrometry.net's.
MAX_RTREE_DISTANCE = 2.0

# Vizier database lookup object.
vizier = Vizier(columns=['_RAJ2000', '_DEJ2000','B-V', 'R2mag', 'B2mag', 'USNO-B1.0'])

def usno_lookup(ra, dec):
    searchstr = '%f %f' % (ra, dec)
    results = cache.get(searchstr)
    if not results:
        results = vizier.query_region(searchstr, radius='1s', catalog='I/284/out')
        if len(results) > 0:
            cache[searchstr] = results
    return results

def choose_reference_stars_from_file(corr_fits_path, point_source_json_path):
    point_source_json = open(point_source_json_path, 'r').read()
    corr_fits_data = open(corr_fits_path, 'rb').read()
    choose_reference_stars(point_source_json, corr_fits_data)

def choose_reference_stars(corr_fits_data, point_source_json):
    '''
    Joins stars found in point source extraction/flux computation step with
    stars from the astrometry step with known J2000 ra, dec.

    Returns: a list of possible reference star objects.
    '''

    logger.info('Matching reference stars with StarFind output...')

    # TODO(ian): Is this whole step even necessary? Why not just use our PSE
    # coords rather than relying on astrometry's?

    # First, load extracted point sources.
    pse_points = json.loads(point_source_json)

    # Then corr file.
    # corr.fits from astrometry.net. See https://groups.google.com/forum/#!topic/astrometry/Lk1LuhwBBNU
    im = fits.open(StringIO(corr_fits_data))
    data = im[1].data

    # And build a lookup tree out of the astrometry corr data.
    tree = rTreeIndex.Index()
    num_rows = 0
    for count, row in np.ndenumerate(data):
        rowdata = dict(zip(data.names, row))
        coords = (rowdata['field_x'], rowdata['field_y'])
        tree.insert(count[0], coords, obj=rowdata)
        num_rows += 1
    logger.info('Coords rtree loaded %d objects' % num_rows)

    # Now, for each extracted point source, try to find its (ra, dec). If so,
    # include it as a possible reference star.

    # Keep track of distance between nearest match.
    distances = []
    reference_objects = []
    for point in pse_points:
        pse_x = point['field_x']
        pse_y = point['field_y']

        # est_mag = -2.5 * log10(est_flux)
        mag_instrumental = point['est_mag']

        nearest = list(tree.nearest((pse_x, pse_y), num_results=1, objects=True))[0].object

        dist = math.sqrt((pse_x - nearest['field_x'])**2 + (pse_y - nearest['field_y'])**2)
        if dist > MAX_RTREE_DISTANCE:
            #logger.error('Rejecting a point source because its distance to nearest corr object is %f, greater than %f' % \
            #             (dist, MAX_RTREE_DISTANCE))
            continue
        distances.append(dist)

        reference_objects.append({
            'field_x': pse_x,
            'field_y': pse_y,
            'index_ra': nearest['index_ra'],
            'index_dec': nearest['index_dec'],
            'mag_i': point['est_mag'],   # Instrumental magnitude
        })

    logger.info('distance count: %d' % len(distances))
    logger.info('distance avg (px): %f' % np.mean(distances))
    logger.info('distance std: %f' % np.std(distances))
    logger.info('distance min: %f' % min(distances))
    logger.info('distance max: %f' % max(distances))
    return reference_objects

def get_standard_magnitudes(reference_objects):
    '''
    Given a list of reference star objects {index_ra, index_dec}, look them up
    in USNO catalog.

    Returns: a list of {designation, reference_Rmag, and optionally
    instrumental_mag, field_x, field_y} objects.
    '''
    logger.info('Running catalog lookups...')
    ret = []
    for comparison_star in reference_objects:
        ra = comparison_star['index_ra']
        dec = comparison_star['index_dec']

        mag_i = comparison_star.get('mag_i')

        # Query USNO catalog.
        results = usno_lookup(ra, dec)
        if len(results) < 1:
            continue
        r2mag = float(results[0]['R2mag'].data[0])
        if math.isnan(r2mag):
            # logger.info('  --> skipping due to no r2mag')
            continue
        desig = results[0]['USNO-B1.0'].data[0]

        obj = {
            'designation': desig,
            'reference_Rmag': r2mag,

            # 'observed_flux': flux,
        }
        if mag_i:
            obj['instrumental_mag'] = mag_i
            obj['field_x'] = comparison_star['field_x'],
            obj['field_y'] = comparison_star['field_y'],
        ret.append(obj)

    return ret

def compute_apparent_magnitudes(reference_objects):
    logger.info('Running catalog lookups...')
    comparison_objs = get_standard_magnitudes(reference_objects)

    logger.info('Running comparisons...')
    percent_errors = []
    for i in range(len(comparison_objs)):
        comparisons = comparison_objs[:]
        target = comparisons[i]
        del comparisons[i]

        comparison_diffs = 0
        target_mags = []
        for comparison in comparisons:
            #instrumental_target_mag = -2.5 * math.log10(target['observed_flux'])
            #instrumental_mag_comparison = -2.5 * math.log10(comparison['observed_flux'])
            instrumental_target_mag = target['instrumental_mag']
            instrumental_mag_comparison = comparison['instrumental_mag']

            # Compute basic standard magnitude formula from Brian Warner.
            target_mag = (instrumental_target_mag - instrumental_mag_comparison) + comparison['reference_Rmag']
            target_mags.append(target_mag)
            # logger.info('computed', target_mag, 'vs actual', target['reference_Rmag'])

            comparison_diffs += instrumental_target_mag - instrumental_mag_comparison

        # Compute differential magnitude.
        comparison_mean = np.mean(comparison_diffs)
        comparison_std = np.std(comparison_diffs)
        # logger.info('comparison magnitude diff average:', comparison_mean)
        # logger.info('comparison magnitude diff std:', comparison_std)

        target_mag_avg = np.mean(target_mags)
        target_mag_std = np.std(target_mags)
        # logger.info('mag target average:', target_mag_avg, 'vs actual', target['reference_Rmag'])
        # logger.info('mag target std:', target_mag_std)

        percent_error = abs(target['reference_Rmag'] - target_mag_avg) / target['reference_Rmag'] * 100.0
        percent_errors.append(percent_error)
        # logger.info('  --> difference:', (target_mag_avg - target['reference_Rmag']))
        # logger.info('  --> % error:', percent_error)

    logger.info('=' * 80)
    logger.info('num comparison objs submitted:', len(reference_objects))
    logger.info('num comparison objs used:', len(comparison_objs))
    logger.info('percent error avg (MAPE):', np.mean(percent_errors))
    logger.info('percent error max:', max(percent_errors))
    logger.info('percent error min:', min(percent_errors))

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
    reference_objects = choose_reference_stars_from_file(args.corr_fits, args.point_source_json)
    compute_apparent_magnitudes(reference_objects)
