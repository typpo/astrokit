import numpy as np
import matplotlib.pyplot as plt

from imageflow.s3_util import upload_to_s3

def compute_tf_from_analysis(analysis, graph_output_path):
    apparent_mags = []
    standard_mags = []
    colors_1 = []
    colors_2 = []
    for star in analysis.catalog_reference_stars:
        apparent_mags.append(star['instrumental_mag'])
        standard_mags.append(star[analysis.image_filter.urat1_key])
        colors_1.append(star[analysis.color_index_1.urat1_key])
        colors_2.append(star[analysis.color_index_2.urat1_key])

    tf, (xs, ys, A, c) = compute_tf(apparent_mags, standard_mags, colors_1, colors_2)

    tf_graph_url = None
    if graph_output_path:
        plt.plot(xs, ys, '+', label='Original data', markersize=10)
        plt.plot(xs, m*xs + c, 'r', label='Fitted line')
        plt.xlabel('%s - %s' % (analysis.color_index_1.band , analysis.color_index_2.band))
        plt.ylabel('M - m')
        plt.legend()
        plt.savefig(graph_output_path)

        # TODO(ian): Upload graph to s3

    return tf, tf_graph_url

def compute_tf(apparent_mags, standard_mags, colors_1, colors_2):
    # Reference: https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.lstsq.html
    xs = np.array(standard_mags) - np.array(apparent_mags)
    ys = np.array(colors_1) - np.array(colors_2)
    A = np.vstack([xs, np.ones(len(xs))]).T
    m, c = np.linalg.lstsq(A, ys)[0]

    return m, (xs, ys, A, c)

def test():
    compute_tf([0, .5, 1, 1.5],
               [0, 1, 2, 3],
               [1, 1, 1, 1],
               [-2, -1.2, -1.9, 1.1],
               graph_output_path='/tmp/tf.png')

if __name__ == '__main__':
    test()

