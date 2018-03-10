#!/usr/bin/env python
#
# Usage: ./run_image_reductions.py [analysis_id]
#

import logging
import os
import sys

import django
import numpy as np

from django.core.exceptions import ObjectDoesNotExist

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

import airmass
import corrections

from imageflow.models import Reduction, ImageAnalysis, ImageFilter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def supporting_calculations(analysis, reduction):
    '''Compute a variety of terms for the main photometry reduction equation.
    '''
    reduction.reduced_stars = analysis.annotated_point_sources[:]

    # Airmass
    airmass.annotate_with_airmass(analysis, reduction)

    # Compute lighttime correction.
    analysis.image_jd_corrected = corrections.get_lighttime_correction(analysis)

def run_reductions(analysis):
    '''Run reductions on a given ImageAnalysis.
    '''
    reduction = analysis.get_or_create_reduction()
    supporting_calculations(analysis, reduction)

    # Get the URAT1 keys for each CI band. eg. 'Bmag', 'jmag'
    filter_key = analysis.image_filter.urat1_key
    ci1_key = reduction.color_index_1.urat1_key
    ci2_key = reduction.color_index_2.urat1_key

    # Get the set of comparison stars.  These are a subset of reduced stars.
    comparison_ids = set(reduction.comparison_star_ids)

    # Now put it all together.
    for i in xrange(len(reduction.reduced_stars)):
        # Assume this star is our target (in reality, there is 1 true target
        # and N reference stars)
        star = reduction.reduced_stars[i]

        if 'color_index' not in star and reduction.color_index_manual is None:
            # This point source was unknown AND it is not our target, so it
            # doesn't have color index.
            continue

        # Mt = (mt - mc) - k"f Xt (CIt - CIc) + Tf (CIt - CIc) + Mc
        estimates = []
        for j in xrange(len(reduction.reduced_stars)):
            if i == j:
                continue

            comparison_star = reduction.reduced_stars[j]
            if comparison_star['id'] not in comparison_ids:
                # This star isn't a comparison star.
                continue
            if comparison_star['id'] == analysis.target_id:
                # The data generated here is for an unknown, so don't use it
                # for a comparison star.
                continue
            if comparison_star['id'] == star['id']:
                # Don't compare a star against itself.
                continue
            if 'color_index_known' not in comparison_star and reduction.color_index_manual is None:
                # TODO(ian): This and the below test should cause an error,
                # because the user chose a bad comparison star.

                # This point source doesn't have a catalog color index, so we
                # don't trust it even though we may have computed its color
                # index.
                continue
            if filter_key not in comparison_star:
                # This point source doesn't have data from the filter we want
                # to convert to.
                continue

            term1 = star['mag_instrumental'] - comparison_star['mag_instrumental']

            # TODO(ian): Use manually entered ci value.
            if reduction.color_index_manual is not None:
                logger.info('Using manual color index %f' % reduction.color_index_manual)
                ci_diff = reduction.color_index_manual
            else:
                ci_target = star['color_index']
                ci_comparison = comparison_star['color_index_known']
                ci_diff = ci_target - ci_comparison

            term2 = reduction.second_order_extinction * star['airmass'] * ci_diff
            term3 = reduction.tf * ci_diff
            mc = comparison_star[filter_key]

            combined = term1 - term2 + term3 + mc
            estimates.append(combined)

            comparison_star['is_comparison'] = True

        star['mag_standard'] = np.mean(estimates)
        star['mag_std'] = np.std(estimates)

        # Set mag_catalog to the URAT1 magnitude in this band.
        if filter_key in star:
            star['mag_catalog'] = star[filter_key]
            star['mag_error'] = star['mag_standard'] - star['mag_catalog']
        else:
            #logger.info('No filter %s in star %s' % (filter_key, star))
            pass

    reduction.status = Reduction.COMPLETE
    reduction.save()

    analysis.status = ImageAnalysis.REDUCTION_COMPLETE
    analysis.save()

    logger.info('Completed reduction %d for analysis %d' % (reduction.id, analysis.id))

def process_pending_reductions():
    pending = Reduction.objects.filter(status=Reduction.PENDING)
    for reduction in pending:
        if reduction.analysis.target_id != 0:
            run_reductions(reduction.analysis)

if __name__ == '__main__':
    import os
    import django
    from django.core.exceptions import ObjectDoesNotExist
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    sys.path.insert(0, os.getcwd())
    django.setup()

    from imageflow.models import ImageAnalysis

    if len(sys.argv) > 1:
        analid = sys.argv[1]
        try:
            analysis = ImageAnalysis.objects.get(pk=analyid)
        except ObjectDoesNotExist:
            logger.info('Could not find analysis %d' % analid)
            sys.exit(1)
        run_reductions(analysis)
    else:
        # Run all pending reductions.
        process_pending_reductions()
