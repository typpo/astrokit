#!/usr/bin/env python

import os
import sys

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

import airmass
import transformation_coefficient as tf

from imageflow.models import Reduction, ImageFilter

def run_reductions(analysis):
    '''Run reductions on a given AnalysisResult and attach airmass to the
    catalog reference stars.
    '''

    reduction = Reduction(color_index_1=ImageFilter.objects.get(band='B'),
                          color_index_2=ImageFilter.objects.get(band='V'))

    # Airmass
    reduction.reduced_stars = airmass.compute_airmass_for_analysis(analysis, reduction)

    # Transformation coefficient
    computed_tf, tf_graph_url = tf.compute_tf_for_analysis(analysis, reduction, '/tmp/tf_graph.png')
    reduction.transformation_coefficient = computed_tf
    analysis.transformation_coefficient_graph_url = tf_graph_url

    reduction.save()

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
