import numpy as np
import matplotlib.pyplot as plt

from imageflow.s3_util import upload_to_s3

def compute_tf_from_analysis(analysis):
    # TODO(ian): join catalog stars with image stars
    pass

def compute_tf(apparent_mags, standard_mags, colors_1, colors_2, graph_output_path=None):
    # Reference: https://docs.scipy.org/doc/numpy-1.13.0/reference/generated/numpy.linalg.lstsq.html
    xs = np.array(standard_mags) - np.array(apparent_mags)
    ys = np.array(colors_1) - np.array(colors_2)
    A = np.vstack([xs, np.ones(len(xs))]).T
    m, c = np.linalg.lstsq(A, ys)[0]

    if graph_output_path:
        plt.plot(xs, ys, 'o', label='Original data', markersize=10)
        plt.plot(xs, m*xs + c, 'r', label='Fitted line')
        plt.legend()
        plt.show()

    return m

def test():
    compute_tf([0, .5, 1, 1.5],
               [0, 1, 2, 3],
               [1, 1, 1, 1],
               [-2, -1.2, -1.9, 1.1],
               graph_output_path=True)

if __name__ == '__main__':
    test()

