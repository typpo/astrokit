import shutil
import subprocess
import tempfile

class Executable(object):
    def __init__(binpath, working_dir=None):
        self._binpath = binpath
        self._working_dir = working_dir
        self._using_temp_working_dir = False

        if not working_dir:
            self._create_temp_working_dir()

    def run(self, image_path, params, config):
        raise NotImplementedError('You must subclass astromatic.Executable')

    def _create_temp_working_dir(self):
        self._working_dir = tempfile.mkdtemp()
        self._using_temp_working_dir = True

    def _remove_temp_working_dir(self):
        if not self._using_temp_working_dir:
            raise RuntimeError('Trying to remove temp working dir but we did not create one')
        shutil.rmtree(self._working_dir)

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

    def __init__(self, working_dir=None):
        super(Sextractor, self).__init__('sextractor', working_dir)
        self._catalog_path = None

    def run(self, image_path, params=[], config={}):
        self._catalog_path = None

        base_name = int(time.time()) + '_' + ''.join([random.choice(string.letters) for _ in range(10)])
        params = DEFAULT_PARAMS if len(params) == 0 else params
        config = self._get_default_config.update(config)

        # Build params
        params_path = os.path.join(self._working_dir, config['PARAMETERS_NAME'])
        with open(params_path, 'w') as f:
            f.write('\n'.join(params))

        # Build config
        config_path = os.path.join(self._working_dir, '%s.sex')
        with open(config_path, 'w') as f:
            f.write('\n'.join(['%s\t%s' % (k, str(v)) for (k, v) in config.items()]))

        # Build args
        args = [self._binpath, '-c', config_path]
        subprocess.call(args, cwd=self._working_dir)

        self._catalog_path = config['CATALOG_NAME']

    def get_catalog_path(self):
        return self._catalog_path

    def get_working_dir(self):
        return self._working_dir

    def _get_default_config(self, basename):
        return {
            'CATALOG_NAME': '%s.cat' % base_name,
            'PARAMETERS_NAME': '%s.param' % base_name,
            'CATALOG_TYPE': 'FITS_LDAC',
        }

def main():
    sex = Sextractor('.')
    params = Sextractor.PREPSF_PARAMS
    config = {
        'PHOT_APERTURES': 11,
        'GAIN': 0.0,
        'PIXEL_SCALE', 2.23,
    }
    sex.run('A771.FIT', params, config)
