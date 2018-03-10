import logging
from cStringIO import StringIO

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

from imageflow.s3_util import upload_to_s3
from reduction.util import average_instrumental_mags_by_desig, find_star_by_designation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run(lightcurve, reduction):
    ci1 = lightcurve.get_ci_band1()
    ci2 = lightcurve.get_ci_band2()

    # Select analyses that match the lightcurve filter.
    image_pairs = ImageAnalysisPair.objects.filter(lightcurve=lightcurve)
    analyses_band1 = [pair.analysis1 for pair in image_pairs]
    analyses_band2 = [pair.analysis2 for pair in image_pairs]

    # TODO(ian): Assert that these analyses are equal to lightcurve ci1, ci2
    # respectively.

    # Take the average instrumental magnitudes for comparison stars across
    # these analyses.
    desig_map_band1 = average_instrumental_mags_by_desig(analyses_band1,
                                                         lightcurve.comparison_star_designations)
    desig_map_band2 = average_instrumental_mags_by_desig(analyses_band2,
                                                         lightcurve.comparison_star_designations)
    stars_band1 = desig_map_band1.values()
    stars_band2 = desig_map_band2.values()
    star_pairs = zip(stars_band1, stars_band2)

    ht, ht_intercept, ht_std, ht_r, ht_url = \
            calculate_hidden_transform(lightcurve, star_pairs, save_graph=True)

    reduction.hidden_transform = ht
    reduction.hidden_transform_intercept = ht_intercept
    reduction.hidden_transform_std = ht_std
    reduction.hidden_transform_rval = ht_r
    reduction.hidden_transform_graph_url = ht_url

    calculate_color_index(lightcurve, reduction, image_pairs)
    #annotate_color_index(analysis, reduction)

def calculate_hidden_transform(lightcurve, star_pairs, save_graph=False):
    # Get the URAT1 keys for each filter and CI band. eg. 'Bmag', 'jmag'
    ci1 = lightcurve.get_ci_band1()
    ci2 = lightcurve.get_ci_band2()
    ci1_key = ci1.urat1_key
    ci2_key = ci2.urat1_key

    standard_diffs = []
    instrumental_diffs = []
    for i in xrange(len(pairs)):
        star1 = stars_band1[i]
        star2 = stars_band2[i]

        assert star['designation'] == star2['designation'], 'Star pair mismatch'

        standard_diffs.append(star1[ci1_key] - star1[ci2_key])
        instrumental_diffs.append(star1['mag_instrumental'] - star2['mag_instrumental'])

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

        graph_url = upload_graph(lightcurve, img_graph.getvalue())
        logger.info('  -> Uploaded to %s' % graph_url)

    return slope, intercept, std_err, r_value, graph_url

def upload_graph(lightcurve, img_graph):
    logger.info('-> Uploading hidden transform graph for lightcurve %d' % (lightcurve.id))

    upload_key_prefix = 'processed/lightcurve/%d' % (lightcurve.id)

    name = 'hidden_transform_graph.jpg'
    logger.info('  -> Uploading %s...' % name)
    return upload_to_s3(img_graph, upload_key_prefix, name)

def calculate_color_index(lightcurve, reduction, image_pairs):
    if reduction.color_index_manual is not None:
        # User has chosen color index.
        reduction.color_index = reduction.color_index_manual
        reduction.save()
        return

    ci1 = lightcurve.get_ci_band1()
    ci2 = lightcurve.get_ci_band2()

    ci1_key = ci1.urat1_key
    ci2_key = ci2.urat1_key

    #cis = defaultdict(list)
    target_cis = []
    for image_pair in image_pairs:
        analysis1 = image_pair.analysis1
        analysis2 = image_pair.analysis2

        '''
        for comp_desig in lightcurve.comparison_star_designations:
            star1 = find_star_by_designation(analysis1.annotated_point_sources)
            star2 = find_star_by_designation(analysis2.annotated_point_sources)

            ci = star1['mag_instrumental'] - star2['mag_instrumental']
            ci_transformed = reduction.hidden_transform * ci + reduction.hidden_transform_intercept
            cis[comp_desig].append(ci_transformed)
        '''

        target1 = find_point_by_id(analysis1.target_id)
        target2 = find_point_by_id(analysis2.target_id)
        ci = target1['mag_instrumental'] - target2['mag_instrumental']
        ci_transformed = reduction.hidden_transform * ci + reduction.hidden_transform_intercept
        target_cis.append(ci_transformed)

    #color_index_by_desig = {}
    # TODO(ian): Show comparison standard color index vs computed color index
    # TODO(ian): Produce graph... (see pg 122)

    reduction.color_index = np.mean(target_cis)
    reduction.save()
