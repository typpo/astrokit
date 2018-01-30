#!/usr/bin/env python

import argparse
import json
import logging
import math
import os
import shelve
import simplejson as json

from cStringIO import StringIO
from decimal import Decimal, InvalidOperation

import numpy as np

from astropy.io import fits
from astroquery.vizier import Vizier
from rtree import index as rTreeIndex

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'cache/catalog.db')
cache = shelve.open(cache_path)

# Maximum distance, in pixels, to accept a match for an object between our
# point source extraction and astrometry.net's.
MAX_RTREE_DISTANCE = 2.0

def urat1_lookup(ra, dec):
    # TODO(ian): Clean all this up and remove duplicate code and field names.
    vizier = Vizier(columns=['URAT1', '_RAJ2000', '_DEJ2000', 'Jmag', 'Hmag', 'Kmag', 'Bmag', 'Vmag', 'gmag', 'rmag', 'imag'])
    catalog = 'I/329'
    searchstr = '%f %f' % (ra, dec)
    cachekey = '%s__%s' % (catalog, searchstr)
    results = cache.get(cachekey)
    if not results:
        results = vizier.query_region(searchstr, radius='1s', catalog=catalog)
        if len(results) > 0:
            cache[cachekey] = results
    return results

def urat1_postprocess(obj):
    if 'Bmag' in obj and 'Vmag' in obj:
        obj['delta_BV'] = obj['Bmag'] - obj['Vmag']
    if 'gmag' in obj and 'rmag' in obj:
        obj['delta_gr'] = obj['gmag'] - obj['rmag']
    return obj

def choose_reference_stars_from_file(corr_fits_path, point_source_json_path):
    point_source_json = open(point_source_json_path, 'r').read()
    corr_fits_data = open(corr_fits_path, 'rb').read()
    return choose_reference_stars(corr_fits_data, point_source_json)

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
    pse_points = json.loads(point_source_json, use_decimal=True)

    # Then corr file.
    # corr.fits from astrometry.net. See https://groups.google.com/forum/#!topic/astrometry/Lk1LuhwBBNU
    # See also: https://groups.google.com/forum/#!topic/astrometry/UtpBHvjBXbM
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
        # These are Decimal typed.
        pse_x = point['field_x']
        pse_y = point['field_y']

        # mag_instrumental = -2.5 * log10(flux)
        mag_instrumental = point['mag_instrumental']

        nearest = list(tree.nearest((pse_x, pse_y), num_results=1, objects=True))[0].object

        dist = math.sqrt((pse_x - Decimal(nearest['field_x']))**2 + (pse_y - Decimal(nearest['field_y']))**2)
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
            'mag_instrumental': point['mag_instrumental'],   # Instrumental magnitude
        })

    logger.info('distance count: %d' % len(distances))
    logger.info('distance avg (px): %f' % np.mean(distances))
    logger.info('distance std: %f' % np.std(distances))
    logger.info('distance min: %f' % min(distances))
    logger.info('distance max: %f' % max(distances))
    return reference_objects

def get_standard_magnitudes_urat1(reference_objects):
    return get_standard_magnitudes(reference_objects,
            'URAT1',
            ['Jmag', 'Hmag', 'Kmag', 'Bmag', 'Vmag', 'gmag', 'rmag', 'imag'],
            urat1_lookup,
            urat1_postprocess)

def get_standard_magnitudes(reference_objects, desig_field, fields, lookup_fn, postprocess_fn):
    '''
    Given a list of reference star objects {index_ra, index_dec}, look them up
    using provided function.

    Returns: a list of {designation, rmag, and optionally
    mag_instrumental, field_x, field_y} objects.
    '''
    logger.info('Running catalog lookups %s...' % desig_field)
    ret = []
    for comparison_star in reference_objects:
        ra = comparison_star['index_ra']
        dec = comparison_star['index_dec']

        mag_i = comparison_star.get('mag_instrumental')

        results = lookup_fn(ra, dec)
        if len(results) < 1:
            continue
        if len(results) > 1:
            logger.warn('Warning: multiple matches for a single point coordinate.')

        result = results[0]
        desig = result[desig_field].data[0]
        obj = {
            'designation': desig,
            'index_ra': ra,
            'index_dec': dec,
        }
        for field in fields:
            strvalue = str(result[field].data[0])
            try:
                obj[field] = Decimal(strvalue)
            except InvalidOperation:
                logger.warn('Encountered bad field for %s: %s = %s' % (json.dumps(obj), field, strvalue))
        if mag_i:
            obj['mag_instrumental'] = mag_i
            obj['field_x'] = comparison_star['field_x'],
            obj['field_y'] = comparison_star['field_y'],
            # TODO(ian): compute standard mag - instrumental mag (for the right band)
        if postprocess_fn:
            obj = postprocess_fn(obj)
        ret.append(obj)

    return ret

def compute_apparent_magnitudes(reference_objects):
    comparison_objs = get_standard_magnitudes_urat1(reference_objects)

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
            #instrumental_comparison_mag = -2.5 * math.log10(comparison['observed_flux'])
            instrumental_target_mag = float(target['mag_instrumental'])
            instrumental_comparison_mag = float(comparison['mag_instrumental'])

            # Compute basic standard magnitude formula from Brian Warner.
            target_mag = (instrumental_target_mag - instrumental_comparison_mag) + comparison['rmag']
            target_mags.append(target_mag)
            # logger.info('computed', target_mag, 'vs actual', target['rmag'])

            comparison_diffs += instrumental_target_mag - instrumental_comparison_mag

        # Compute differential magnitude.
        comparison_mean = np.mean(comparison_diffs)
        comparison_std = np.std(comparison_diffs)
        # logger.info('comparison magnitude diff average:', comparison_mean)
        # logger.info('comparison magnitude diff std:', comparison_std)

        target_mag_avg = np.mean(target_mags)
        target_mag_std = np.std(target_mags)
        # logger.info('mag target average:', target_mag_avg, 'vs actual', target['rmag'])
        # logger.info('mag target std:', target_mag_std)

        percent_error = abs(target['rmag'] - target_mag_avg) / target['rmag'] * 100.0
        percent_errors.append(percent_error)
        # logger.info('  --> difference:', (target_mag_avg - target['rmag']))
        # logger.info('  --> % error:', percent_error)

    logger.info('=' * 80)
    logger.info('num comparison objs submitted: %d' % len(reference_objects))
    logger.info('num comparison objs used: %d' % len(comparison_objs))
    logger.info('percent error avg (MAPE): %f' % np.mean(percent_errors))
    logger.info('percent error max: %f' % max(percent_errors))
    logger.info('percent error min: %f' % min(percent_errors))

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
