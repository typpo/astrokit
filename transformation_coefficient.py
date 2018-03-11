import logging
from collections import defaultdict
from cStringIO import StringIO

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from imageflow.models import ImageAnalysis
from imageflow.s3_util import upload_to_s3
from reduction.util import average_instrumental_mags_by_desig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(lightcurve, reduction):
    # Select analyses that match the lightcurve filter.
    analyses = ImageAnalysis.objects.filter(lightcurve=lightcurve,
                                            image_filter=lightcurve.filter)

    # Take the average instrumental magnitudes for common stars across these
    # analyses.
    desig_map = average_instrumental_mags_by_desig(analyses, lightcurve.get_common_desigs())
    stars = desig_map.values()

    tf_computed, zpf, tf_std, tf_graph_url = calculate(lightcurve, stars, save_graph=True)
    reduction.tf = tf_computed
    # TODO(ian): Brian Warner says 0.015 stderr is higher than preferred, and
    # range of color index should be > .6
    reduction.tf_std = tf_std
    reduction.zpf = zpf
    reduction.tf_graph_url = tf_graph_url
    reduction.save()

def calculate(lightcurve, stars, save_graph=False):
    ci1 = lightcurve.get_ci_band1()
    ci2 = lightcurve.get_ci_band2()

    # Get the URAT1 keys for each filter and CI band. eg. 'Bmag', 'jmag'
    ci1_key = ci1.urat1_key
    ci2_key = ci2.urat1_key
    filter_key = lightcurve.filter.urat1_key

    apparent_mags = []
    standard_mags = []
    colors_1 = []
    colors_2 = []
    for star in stars:
        if not (filter_key in star and ci1_key in star and ci2_key in star):
            print 'Rejecting star because it does not have the required standard magnitudes:', star
            continue

        apparent_mags.append(star['mag_instrumental'])
        standard_mags.append(star[filter_key])
        colors_1.append(star[ci1_key])
        colors_2.append(star[ci2_key])

    (slope, intercept, r_value, p_value, std_err), xs, ys = \
            calculate_tf(apparent_mags, standard_mags, colors_1, colors_2)
    tf = slope
    zpf = intercept

    tf_graph_url = None
    if save_graph:
        band1 = ci1.band.upper()
        band2 = ci2.band.upper()

        # Clear any existing state
        plt.clf()
        plt.cla()
        plt.close()

        plt.title(r'$%s = %s_0 + %f(%s-%s) + %f\ \ \ \ s.d. %f\ mag$' % \
                    (band1, band1.lower(), tf, band1, band2, zpf, std_err))
        plt.plot(xs, ys, '+', label='Original data', markersize=10)
        plt.plot(xs, tf*xs + zpf, 'r', label='Fitted line')

        plt.xlabel('%s-%s (catalog)' % (band1, band2))
        plt.ylabel(r'$M-m_0$')

        img_graph = StringIO()
        plt.savefig(img_graph)

        tf_graph_url = upload_graph(lightcurve, img_graph.getvalue())
        logger.info('  -> Uploaded to %s' % tf_graph_url)

    return tf, zpf, std_err, tf_graph_url

def calculate_tf(apparent_mags, standard_mags, colors_1, colors_2):
    xs = np.array(colors_1) - np.array(colors_2)
    ys = np.array(standard_mags) - np.array(apparent_mags)
    return stats.linregress(xs, ys), xs, ys

def upload_graph(lightcurve, img_graph):
    logger.info('-> Uploading tf graph for submission %d' % (submission.subid))

    upload_key_prefix = 'processed/lightcurve/%d' % (lightcurve.id)

    name = 'tf_graph.jpg'
    logger.info('  -> Uploading %s...' % name)
    return upload_to_s3(img_graph, upload_key_prefix, name)
