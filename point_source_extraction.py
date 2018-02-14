#!/usr/bin/env python2.7
'''
Point-source extraction.

Usage: python point_source_extraction.py myimage.fits
'''

import logging
import simplejson as json
import urllib

from cStringIO import StringIO

import matplotlib.pylab as plt
import numpy as np

from PIL import Image
from astropy.io import fits
from astropy.modeling.fitting import LevMarLSQFitter
from astropy.stats import gaussian_sigma_to_fwhm
from photutils import CircularAperture
from photutils.background import MMMBackground, MADStdBackgroundRMS
from photutils.detection import IRAFStarFinder
from photutils.psf import IntegratedGaussianPRF, DAOGroup, IterativelySubtractedPSFPhotometry, DAOPhotPSFPhotometry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def compute(settings, image_data):
    # Taken from photuils example http://photutils.readthedocs.io/en/stable/psf.html
    # See also http://photutils.readthedocs.io/en/stable/api/photutils.psf.DAOPhotPSFPhotometry.html#photutils.psf.DAOPhotPSFPhotometry

    sigma_psf = settings.sigma_psf
    crit_separation = settings.crit_separation
    threshold = settings.threshold
    box_size = settings.box_size
    niters = settings.iters

    bkgrms = MADStdBackgroundRMS()
    std = bkgrms(image_data)

    logger.info('Using sigma=%f, threshold=%f, separation=%f, box_size=%d, niters=%d' % \
                (sigma_psf, threshold, crit_separation, box_size, niters))
    photargs = {
	'crit_separation': crit_separation * sigma_psf,
	'threshold': threshold * std,
	'fwhm': sigma_psf * gaussian_sigma_to_fwhm,
	'fitter': LevMarLSQFitter(),
	'niters': niters,
	'fitshape': (box_size, box_size),
    }

    photargs['psf_model'] = IntegratedGaussianPRF(sigma=sigma_psf)
    # photargs['psf_model'].sigma.fixed = False

    photometry = DAOPhotPSFPhotometry(**photargs)

    # Column names:
    # 'flux_0', 'x_fit', 'x_0', 'y_fit', 'y_0', 'flux_fit', 'id', 'group_id',
    # 'flux_unc', 'x_0_unc', 'y_0_unc', 'iter_detected'
    result_tab = photometry(image=image_data)
    # Formula: https://en.wikipedia.org/wiki/Instrumental_magnitude
    result_tab['mag'] = -2.5 * np.log10(result_tab['flux_fit'])

    residual_image = photometry.get_residual_image()

    # TODO(ian): Return uncertainty and other information.
    return result_tab, residual_image, (0, 0, std)

def save_image(data, path):
    # FIXME(ian): This is not trustworthy.
    width_height = (len(data[0]), len(data))
    img = Image.new('L', width_height)
    flatdata = np.asarray(data.flatten())
    img.putdata(flatdata)
    img.save(path)

def plot(sources, data, path):
    positions = (sources['x_fit'], sources['y_fit'])
    # TODO(ian): Show fwhm as aperture size.
    apertures = CircularAperture(positions, r=4.)
    #norm = ImageNormalize(stretch=SqrtStretch())
    plt.clf()
    plt.imshow(data, cmap='Greys', origin='lower') #, norm=norm)
    apertures.plot(color='blue', lw=1.5, alpha=0.5)

    plt.savefig(path)

def save_fits(sources, path):
    col_x = fits.Column(name='field_x', format='E', array=sources['x_fit'])
    col_y = fits.Column(name='field_y', format='E', array=sources['y_fit'])
    flux = fits.Column(name='flux', format='E', array=sources['flux_fit'])
    mag_instrumental = fits.Column(name='mag_instrumental', format='E', array=sources['mag'])

    cols = fits.ColDefs([col_x, col_y, flux, mag_instrumental])
    tbhdu = fits.BinTableHDU.from_columns(cols)
    tbhdu.writeto(path, clobber=True)

def format_for_json_export(sources):
    field_x = sources['x_fit']
    field_y = sources['y_fit']
    flux = sources['flux_fit']
    mag_instrumental = sources['mag']

    out = []
    for i in xrange(len(field_x)):
        out.append({
            'id': i + 1,
            'field_x': float(field_x[i]),
            'field_y': float(field_y[i]),
            'flux': float(flux[i]),
            'mag_instrumental': float(mag_instrumental[i]),
        })
    return out

def save_json(sources, path):
    out = format_for_json_export(sources)
    with open(path, 'w') as f:
        f.write(json.dumps(out, indent=2, use_decimal=True))

def compute_psf_flux(image_data, sources, \
        scatter_output_path=None, bar_output_path=None, hist_output_path=None, \
        residual_path=None):
    logger.info('Computing flux...')
    coords = zip(sources['x_fit'], sources['y_fit'])

    #psf_gaussian = GaussianPSF(1)
    #computed_fluxes = psf_photometry(image_data, coords, psf_gaussian)
    #computed_fluxes_sorted = sorted(computed_fluxes)

    '''
    if scatter_output_path:
        logger.info('Saving scatter plot...')
        plt.close('all')
        plt.scatter(sorted(sources['flux_fit']), computed_fluxes_sorted)
        plt.xlabel('Fluxes catalog')
        plt.ylabel('Fluxes photutils')
        plt.savefig(scatter_output_path)

    if bar_output_path:
        logger.info('Saving bar chart...')
        plt.close('all')
        plt.bar(xrange(len(computed_fluxes)), computed_fluxes_sorted[::-1])
        plt.ylabel('Flux')
        plt.savefig(bar_output_path)

    if hist_output_path:
        logger.info('Saving histogram...')
        plt.close('all')
        plt.hist(computed_fluxes, bins=50)
        plt.xlabel('Flux')
        plt.ylabel('Frequency')
        plt.savefig(hist_output_path)

    if residual_path:
        residuals = subtract_psf(np.float64(image_data.copy()), psf_gaussian, coords, computed_fluxes)

        # Plot it.
        plt.close('all')
        plt.imshow(residuals, interpolation='None', origin='lower')
        #plt.plot(coords[0], coords[1], marker='o', markerfacecolor='None', markeredgecolor='y', linestyle='None')
        #plt.colorbar(orientation='horizontal')
        plt.savefig(residual_path)
    '''

def load_image(path):
    return extract_image_data_from_fits(fits.open(path))
    #return fits.getdata(path)

def load_url(url):
    page = urllib.urlopen(url)
    content = page.read()
    return extract_image_data_from_fits(fits.open(StringIO(content)))
    #return fits.getdata(StringIO(content))

def extract_image_data_from_fits(im):
    if len(im[0].data) == 3:
        # Sometimes the resulting image is 3 dimensional.
        return im[0].data[2]
    # Sometimes it's just a normal image.
    return im[0].data
