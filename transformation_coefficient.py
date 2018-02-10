import logging
from cStringIO import StringIO

import numpy as np
import matplotlib.pyplot as plt

from imageflow.s3_util import upload_to_s3

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute_tf_for_analysis(analysis, reduction, save_graph=False):
    apparent_mags = []
    standard_mags = []
    colors_1 = []
    colors_2 = []
    for star in analysis.catalog_reference_stars:
        # Get the URAT1 keys for each filter and CI band. eg. 'Bmag', 'jmag'
        filter_key = analysis.image_filter.urat1_key
        ci1_key = reduction.color_index_1.urat1_key
        ci2_key = reduction.color_index_2.urat1_key

        if not (filter_key in star and ci1_key in star and ci2_key in star):
            print 'Rejecting star because it does not have the required standard magnitudes:', star
            continue

        apparent_mags.append(star['mag_instrumental'])
        standard_mags.append(star[filter_key])
        colors_1.append(star[ci1_key])
        colors_2.append(star[ci2_key])

    tf, (xs, ys, A, c) = compute_tf(apparent_mags, standard_mags, colors_1, colors_2)

    tf_graph_url = None
    if save_graph:
        plt.plot(xs, ys, '+', label='Original data', markersize=10)
        plt.plot(xs, tf*xs + c, 'r', label='Fitted line')
        plt.xlabel('%s - %s' % (reduction.color_index_1.band , reduction.color_index_2.band))
        plt.ylabel('M - m')
        plt.legend()

        img_graph = StringIO()
        plt.savefig(img_graph)

        tf_graph_url = upload_graph(analysis, reduction, img_graph.getvalue())
        logger.info('  -> Uploaded to %s' % tf_graph_url)

    return tf, tf_graph_url

def compute_tf(apparent_mags, standard_mags, colors_1, colors_2):
    # Reference: https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.lstsq.html
    xs = np.array(colors_1) - np.array(colors_2)
    ys = np.array(standard_mags) - np.array(apparent_mags)
    A = np.vstack([xs, np.ones(len(xs))]).T
    m, c = np.linalg.lstsq(A, ys)[0]

    return m, (xs, ys, A, c)

def upload_graph(analysis, reduction, img_graph):
    job = analysis.astrometry_job
    submission = job.submission

    logger.info('-> Uploading tf graph for submission %d' % (submission.subid))

    upload_key_prefix = 'processed/%d' % (submission.subid)

    name = '%d_%d_tf_graph.jpg' % (submission.subid, job.jobid)
    logger.info('  -> Uploading %s...' % name)
    return upload_to_s3(img_graph, upload_key_prefix, name)

def test():
    compute_tf([0, .5, 1, 1.5],
               [0, 1, 2, 3],
               [1, 1, 1, 1],
               [-2, -1.2, -1.9, 1.1],
               graph_output_path='/tmp/tf.png')

if __name__ == '__main__':
    test()

