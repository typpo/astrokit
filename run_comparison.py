#!/usr/bin/env python
#
# Computes comparison stars for lightcurves.
# Usage: ./run_comparison.py [lightcurve_id]
#

import logging
import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

from imageflow.models import ImageAnalysis
from lightcurve.models import LightCurve
from reduction.util import find_star_by_designation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_common_stars(analyses):
    '''Returns a list of reference stars that appear in all ImageAnalyses
    '''
    assert len(analyses) > 0, 'Must have at least 1 analysis to get common stars'
    common_star_desigs = set([x['designation'] for x in analyses[0].catalog_reference_stars])
    for analysis in analyses[1:]:
        common_star_desigs.intersection_update(\
                [x['designation'] for x in analysis.catalog_reference_stars])

    # Build data on each star to return.
    ret = []
    for desig in common_star_desigs:
        star = dict(find_star_by_designation(analyses[0].catalog_reference_stars, desig))
        ret.append(star)
    return ret

def process(lightcurve):
    analyses = ImageAnalysis.objects.filter(lightcurve=lightcurve).order_by('image_datetime')

    stars = get_common_stars([analysis for analysis in analyses \
            if analysis.target_id and analysis.target_id > 0])
    lightcurve.common_stars = stars

    # TODO(ian): Be smart about how we choose comparison stars from the common
    # stars. For now, we just make every common star a comparison star.
    lightcurve.comparison_stars = stars

    lightcurve.status = LightCurve.REDUCTION_PENDING
    lightcurve.save()

def process_pending():
    pending = LightCurve.objects.filter(status=LightCurve.PHOTOMETRY_PENDING)
    for lc in pending:
        images = ImageAnalysis.objects.filter(lightcurve=lc)
        if not all([image.is_photometry_complete() for image in images]):
            # Don't process common and comparison stars until all photometry is
            # complete.
            continue
        process(lc)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        lightcurve_id = sys.argv[1]
        try:
            lc = LightCurve(pk=lightcurve_id)
        except ObjectDoesNotExist:
            logger.info('Could not find id %d' % lightcurve_id)
            sys.exit(1)
        run_reductions(lc)
    else:
        # Run all pending reductions.
        process_pending()

    logger.info('Done.')
