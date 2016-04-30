#!/usr/bin/env python2.7
'''
Usage: python photometry_test.py <corr.fits path> <image.fits path>
'''

import sys

import numpy
import astropy.units as u
from astropy.io import fits
from photutils.psf import psf_photometry, GaussianPSF

CORR_PATH = sys.argv[1]
IMAGE_PATH = sys.argv[2]
OUTPUT_PATH = sys.argv[3] if len(sys.argv) > 3 else 'flux_comparison.png'

corr = fits.open(CORR_PATH)
coords = zip(corr[1].data['field_x'], corr[1].data['field_y'])
catalog_fluxes = corr[1].data['FLUX']

# Convert
factor = (u.MJy / u.sr * (0.402 * u.arcsec) ** 2 / u.pixel).to(u.mJy / u.pixel)
catalog_fluxes *= factor.value

im = fits.open(IMAGE_PATH)
data = im[0].data[2]
psf_gaussian = GaussianPSF(1)
computed_fluxes = psf_photometry(data, coords, psf_gaussian)

print len(catalog_fluxes), 'sources present in metadata'

# Check
import matplotlib.pyplot as plt

plt.scatter(catalog_fluxes, computed_fluxes)
plt.xlabel('Fluxes catalog')
plt.ylabel('Fluxes photutils')

#plt.plot(numpy.sort(computed_fluxes)/numpy.sort(catalog_fluxes))
#plt.xlabel('star #')
#plt.ylabel('computed/catalog')

plt.savefig(OUTPUT_PATH)

print 'Done.'
