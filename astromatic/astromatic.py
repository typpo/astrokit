#!/usr/bin/env python

import json
import logging
import os
import shutil
import subprocess
import tempfile

from astropy.io.ascii import SExtractor as SexToAstropy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Executable(object):
    def __init__(self, binpath, working_dir=None, name='unknown'):
        self._binpath = binpath
        self._working_dir = working_dir
        self._using_temp_working_dir = False
        self._name = name

        if not working_dir:
            self._create_temp_working_dir()

    def run(self, image_path, params, config):
        raise NotImplementedError('You must subclass astromatic.Executable')

    def get_working_dir(self):
        return self._working_dir

    def cleanup(self):
        if not self._using_temp_working_dir:
            return
        shutil.rmtree(self._working_dir)

    def _create_temp_working_dir(self):
        self._working_dir = tempfile.mkdtemp()
        self._using_temp_working_dir = True

class Sextractor(Executable):
    DEFAULT_PARAMS = [
        'X_IMAGE',
        'Y_IMAGE',
    ]

    PREPSF_PARAMS = [
	'X_IMAGE',
	'Y_IMAGE',
	'FLUX_RADIUS',
	'FLUX_APER(1)',
	'FLUXERR_APER(1)',
	'ELONGATION',
	'FLAGS',
	'SNR_WIN',
	'VIGNET(35,35)',
    ]

    DEFAULT_CONV = '''CONV NORM
# 3x3 ``all-ground'' convolution mask with FWHM = 2 pixels.
1 2 1
2 4 2
1 2 1'''

    def __init__(self, working_dir=None, name='sex'):
        super(Sextractor, self).__init__('sextractor', working_dir, name)
        self._catalog_path = None
        self._name = name

    def run(self, image_path, params=[], config={}, conv=DEFAULT_CONV):
        logger.info('Configuring Sextractor for image %s' % image_path)
        self._catalog_path = None

        final_params = DEFAULT_PARAMS if len(params) == 0 else params
        final_config = self._get_default_config()
        final_config.update(config)

        # Build params
        params_path = os.path.join(self._working_dir, final_config['PARAMETERS_NAME'])
        with open(params_path, 'w') as f:
            content = '\n'.join(final_params)

            logger.info('Parameters:')
            logger.info('\n' + content)

            f.write(content)

        # Build config
        config_path = os.path.join(self._working_dir, '%s.sex')
        with open(config_path, 'w') as f:
            logger.info('.sex config:')
            logger.info('\n' + json.dumps(final_config, indent=2))

            f.write('\n'.join(['%s\t%s' % (k, str(v)) for (k, v) in final_config.items()]))

        # Build conv
        conv_path = os.path.join(self._working_dir, final_config['FILTER_NAME'])
        with open(conv_path, 'w') as f:
            f.write(conv)

        # Build args
        args = [self._binpath, '-c', config_path, image_path]
        subprocess.call(args, cwd=self._working_dir)

        self._catalog_path = final_config['CATALOG_NAME']

    def get_catalog_path(self):
        return os.path.join(self._working_dir, self._catalog_path)

    def get_astropy_catalog(self):
        return SexToAstropy().read(open(self.get_catalog_path()))

    def _get_default_config(self):
        return {
            'CATALOG_NAME': '%s.cat' % self._name,
            'FILTER_NAME': '%s.conv' % self._name,
            'PARAMETERS_NAME': '%s.param' % self._name,
            'CATALOG_TYPE': 'FITS_LDAC',
        }

class PsfEx(Executable):
    def __init__(self, working_dir=None, name='psfex'):
        super(PsfEx, self).__init__('psfex', working_dir, name)

    def run(self, catalog_paths, config={}):
        final_config = self._get_default_config()
        final_config.update(config)

        # Build config
        config_path = os.path.join(self._working_dir, '%s.psfex')
        with open(config_path, 'w') as f:
            logger.info('.psfex config:')
            logger.info('\n' + json.dumps(final_config, indent=2))

            f.write('\n'.join(['%s\t%s' % (k, str(v)) for (k, v) in final_config.items()]))

        # Build args
        args = [self._binpath, '-c', config_path] + catalog_paths
        subprocess.call(args, cwd=self._working_dir)

    def _get_default_config(self):
        return {
            'PSF_DIR': self._working_dir,
        }

    def get_psf_paths(self):
        return [os.path.join(self._working_dir, path) for path in os.listdir(self._working_dir) \
                if path.endswith('.psf')]

def main():
    thisdir = os.path.dirname(os.path.realpath(__file__))
    fitspath = os.path.join(thisdir, '../examples/a771/A771A001.FIT')

    logger.info('Running sextractor first round...')
    sex1 = Sextractor(name='sex1')
    params = Sextractor.PREPSF_PARAMS
    sex_config = {
        'PHOT_APERTURES': 11,
        'GAIN': 0.0,
        'PIXEL_SCALE': 2.23,
        'SATUR_LEVEL': 50000,
    }
    sex1.run(fitspath, params, sex_config)

    logger.info('Catalog written to %s' % sex1.get_catalog_path())

    logger.info('Running psfefx...')
    psfex = PsfEx()
    psfex.run([sex1.get_catalog_path()])

    logger.info('PSF model written to %s' % psfex.get_psf_paths()[0])
    logger.info('Running sextractor second round...')

    sex2 = Sextractor(name='sex2')
    params = ['X_IMAGE', 'Y_IMAGE', 'MAG_PSF', 'MAGERR_PSF', 'FLUX_PSF',
              'FLUXERR_PSF', 'MAG_BEST', 'MAGERR_BEST']
    sex_config.update({
        'PSF_NAME': psfex.get_psf_paths()[0],
        'CATALOG_TYPE': 'ASCII_HEAD',
    })
    sex2.run(fitspath, params, sex_config)
    logger.info('Final result: %s' % sex2.get_catalog_path())
    logger.info(sex2.get_astropy_catalog())

    sex1.cleanup()
    sex2.cleanup()
    psfex.cleanup()

if __name__ == '__main__':
    main()
