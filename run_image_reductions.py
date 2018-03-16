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
    logger.info('Running reductions for analysis %d' % analysis.id)

    reduction = analysis.get_or_create_reduction()
    lightcurve_reduction = analysis.lightcurve.get_or_create_reduction()
    supporting_calculations(analysis, reduction)

    # Get the URAT1 keys for each CI band. eg. 'Bmag', 'jmag'
    filter_key = analysis.lightcurve.magband.urat1_key

    use_color_index = analysis.lightcurve.ciband != 'NONE'
    if use_color_index:
        ci1_key = analysis.lightcurve.get_ci_band1().urat1_key
        ci2_key = analysis.lightcurve.get_ci_band2().urat1_key

    # Get the set of comparison stars.  These are a subset of reduced stars.
    comparison_stars = analysis.lightcurve.comparison_stars

    # Now put it all together.
    for i in xrange(len(reduction.reduced_stars)):
        # Assume this star is our target (in reality, there is 1 true target
        # and N reference stars)
        star = reduction.reduced_stars[i]

        # Mt = (mt - mc) - k"f Xt (CIt - CIc) + Tf (CIt - CIc) + Mc
        estimates = []
        for comparison_star in comparison_stars:
            if 'designation' in star and comparison_star['designation'] == star['designation']:
                # Don't compare a star against itself.
                continue

            term1 = star['mag_instrumental'] - comparison_star['mag_instrumental']

            # Right now we use the color index computed for the TARGET, not
            # necessarily this star.
            # TODO(ian): Use correct color index for each star.
            if use_color_index:
                ci_target = lightcurve_reduction.color_index_manual
                if not ci_target:
                    # No manual color index, use computed.
                    ci_target = lightcurve_reduction.color_index

                ci_comparison = comparison_star[ci1_key] - comparison_star[ci2_key]
                ci_diff = ci_target - ci_comparison

                term2 = lightcurve_reduction.second_order_extinction * star['airmass'] * ci_diff
                term3 = lightcurve_reduction.tf * ci_diff
            else:
                term2 = 0
                term3 = 0
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
        if reduction.analysis.target_id and reduction.analysis.target_id > 0:
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
