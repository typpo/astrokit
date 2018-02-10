import logging
from cStringIO import StringIO

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from imageflow.s3_util import upload_to_s3
from reduction.util import find_star_by_designation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate(analysis, reduction, save_graph=False):
    companion_image = analysis.reduction.image_companion
    if not companion_image:
        raise Error('You must have a companion image to calculate the hidden transform')

    standard_diffs = []
    instrumental_diffs = []
    for star in analysis.catalog_reference_stars:
        # Get the URAT1 keys for each filter and CI band. eg. 'Bmag', 'jmag'
        filter_key = analysis.image_filter.urat1_key
        ci1_key = reduction.color_index_1.urat1_key
        ci2_key = reduction.color_index_2.urat1_key

        star_in_companion_image = find_star_by_designation(companion_image.analysis, star['designation'])
        if not star_in_companion_image:
            print 'Rejecting star because could not find it in companion image:', star
            continue

        if not (filter_key in star and ci1_key in star and ci2_key in star):
            # TODO(ian): expand this for companion star
            print 'Rejecting star because it does not have the required standard magnitudes:', star
            continue

        standard_diffs.append(star[ci1_key] - star[ci2_key])
        instrumental_diffs.append(star['mag_instrumental'] - star_in_companion_image['mag_instrumental'])

    xs = np.array(instrumental_diffs)
    ys = np.array(standard_diffs)

    slope, intercept, r_value, p_value, std_err = stats.linregress(xs, ys)

    graph_url = None
    if save_graph:
        band1 = reduction.color_index_1.band.upper()
        band2 = reduction.color_index_2.band.upper()

        # Clear any existing state
        plt.clf()
        plt.cla()
        plt.close()

        plt.title(r'$%s-%s = %f(%s-%s) + %f\ \ \ R=%f$' % \
                    (band1, band2, slope, band1.lower(), band2.lower(), intercept, r_value))
        plt.plot(xs, ys, '+', label='Original data', markersize=10)
        plt.plot(xs, slope * xs + intercept, 'r', label='Fitted line')
        plt.xlabel('%s-%s (instrumental)' % (band1.lower(), band2.lower()))
        plt.ylabel('%s-%s (catalog)' % (band1, band2))

        img_graph = StringIO()
        plt.savefig(img_graph)

        graph_url = upload_graph(analysis, reduction, img_graph.getvalue())
        logger.info('  -> Uploaded to %s' % graph_url)

    return slope, intercept, std_err, r_value, graph_url

def upload_graph(analysis, reduction, img_graph):
    job = analysis.astrometry_job
    submission = job.submission

    logger.info('-> Uploading hidden transform graph for submission %d' % (submission.subid))

    upload_key_prefix = 'processed/%d' % (submission.subid)

    name = '%d_%d_hidden_transform_graph.jpg' % (submission.subid, job.jobid)
    logger.info('  -> Uploading %s...' % name)
    return upload_to_s3(img_graph, upload_key_prefix, name)

