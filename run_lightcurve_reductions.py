#!/usr/bin/env python
#
# Usage: ./run_lightcurve_reductions.py [lightcurve_id]
#

import logging
import os
import sys

from collections import defaultdict

import django
import numpy as np

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

import hidden_transform
import transformation_coefficient as tf

from imageflow.models import ImageAnalysis, ImageAnalysisPair
from lightcurve.models import LightCurve, LightCurveReduction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_reduction(lightcurve):
    analysis = ImageAnalysis.objects.filter(lightcurve=lightcurve)
    reduction = lightcurve.get_or_create_reduction()

    # Transformation coefficient.
    tf.run(lightcurve, reduction)

    # Hidden transform.
    hidden_transform.run(lightcurve, reduction)

def process_pending_reductions():
    pending = LightCurve.objects.filter(status=LightCurve.REDUCTION_PENDING)
    for lc in pending:
        run_reduction(lc)

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
        process_pending_reductions()
