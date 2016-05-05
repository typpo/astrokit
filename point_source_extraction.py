#!/usr/bin/env python2.7
'''
Point-source extraction.

Usage: python point_source_extraction.py myimage.fits
'''

import argparse
import sys

import matplotlib.pylab as plt
import numpy

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.visualization import SqrtStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from photutils import CircularAperture
from photutils import datasets, daofind

IMAGE_PATH = sys.argv[1]
OUTPUT_PATH = sys.argv[2] if len(sys.argv) > 2 else 'point_source_extracted.png'

def compute(data):
    mean, median, std = sigma_clipped_stats(data, sigma=3.0, iters=5)

    sources = daofind(data - median, fwhm=3.0, threshold=5.*std)

    print sources
    print len(sources), 'sources'
    print numpy.where(sources['mag'] > 0)
    return sources

def plot(sources, data, path):
    positions = (sources['xcentroid'], sources['ycentroid'])
    apertures = CircularAperture(positions, r=4.)
    norm = ImageNormalize(stretch=SqrtStretch())
    plt.imshow(data, cmap='Greys', origin='lower', norm=norm)
    apertures.plot(color='blue', lw=1.5, alpha=0.5)

    plt.savefig(path)

def load_image(path):
    im = fits.open(IMAGE_PATH)
    data = im[0].data[2]

    # hdu = datasets.load_star_image()
    # data = hdu.data[0:400, 0:400]
    # data = hdu.data
    return data

if __name__ == '__main__':
    image_data = load_image(IMAGE_PATH)
    sources = compute(image_data)
    plot(sources, image_data, OUTPUT_PATH)
    print 'Done.'
