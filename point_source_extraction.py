#!/usr/bin/env python2.7
'''
Point-source extraction.

Usage:
'''

import sys

from photutils import datasets, daofind
from astropy.stats import sigma_clipped_stats

hdu = datasets.load_star_image()

#data = hdu.data[0:400, 0:400]
data = hdu.data
mean, median, std = sigma_clipped_stats(data, sigma=3.0, iters=5)

sources = daofind(data - median, fwhm=3.0, threshold=5.*std)

print sources
