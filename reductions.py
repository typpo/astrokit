#!/usr/bin/env python

import sys

import airmass
import transformation_coefficient as tf

def run_reductions(analysis):
    '''Run reductions on a given AnalysisResult and attach airmass to the
    catalog reference stars.
    '''

    analysis.reduced_stars = airmass.compute_airmass_for_analysis(analysis)

    computed_tf, tf_graph_url = tf.compute_tf_for_analysis(analysis, '/tmp/tf_graph.png')
    analysis.tf = computed_tf
    analysis.tf_graph_url = tf_graph_url

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
