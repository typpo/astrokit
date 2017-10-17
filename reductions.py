#!/usr/bin/env python

import sys

import airmass

def run_reductions(analysis):
    '''Run reductions on a given AnalysisResult and attach airmass to the
    catalog reference stars.
    '''
    annotated_stars = []
    for star in analysis.catalog_reference_stars:
        ra = star['index_ra']
        dec = star['index_dec']
        computed_airmass = airmass.compute_airmass_from_analysis(analysis, ra, dec)
        star['airmass'] = float(computed_airmass)

        annotated_stars.append(star)

    analysis.reference_stars_with_airmass = annotated_stars
    analysis.save()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: reductions.py <submission id>'
        sys.exit(1)

    import os
    import django
    from django.core.exceptions import ObjectDoesNotExist
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    sys.path.insert(0, os.getcwd())
    django.setup()

    from imageflow.models import AnalysisResult
    subid = sys.argv[1]

    try:
        result = AnalysisResult.objects.get( \
                astrometry_job__submission__subid=subid, \
                status=AnalysisResult.COMPLETE)
    except ObjectDoesNotExist:
        print 'Could not find submission', subid
        sys.exit(1)

    run_reductions(result)
