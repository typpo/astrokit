from __future__ import unicode_literals

from collections import OrderedDict

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.db.utils import OperationalError

CI_BAND_TO_FILTERS = OrderedDict([
    ('BV', ('B', 'V')),
    ('VR', ('V', 'R')),
    ('VI', ('V', 'I')),
    ('SGU', ('g', 'u')),
    ('SGR', ('g', 'r')),
    ('SRI', ('r', 'i')),
    ('SIZ', ('i', 'z')),
])

class ImageFilterManager(models.Manager):
    def get_default(self):
        try:
            return self.get(band='B').pk
        except:
            # Happens when db doesn't exist yet, get_default() is called at
            # some imports and it should pass.
            print 'Image filter returning NULL default'
            return None

    def get_default_2(self):
        try:
            return self.get(band='V').pk
        except:
            # Happens when db doesn't exist yet, get_default() is called at
            # some imports and it should pass.
            print 'Image filter returning NULL default'
            return None

    def get_from_ci_band(self, ci_band, pos):
        filters = CI_BAND_TO_FILTERS.get(ci_band)
        if not filters or pos not in [0, 1]:
            return None
        return filters[pos]

    def get_ci_bands(self):
        return CI_BAND_TO_FILTERS.keys()

class ImageFilter(models.Model):
    objects = ImageFilterManager()

    band = models.CharField(max_length=512, unique=True)
    system = models.CharField(max_length=512)
    range_min_nm = models.IntegerField()
    urat1_key = models.CharField(max_length=50)

    def __str__(self):
        return '%s (%s)' % (self.band, self.system)

    def __unicode__(self):
        return u'%s (%s)' % (self.band, self.system)

class PhotometrySettings(models.Model):
    analysis = models.ForeignKey('imageflow.ImageAnalysis')

    sigma_psf = models.FloatField(default=2.0)
    crit_separation = models.FloatField(default=5.0)
    threshold = models.FloatField(default=5.0)
    box_size = models.IntegerField(default=11)
    iters = models.IntegerField(default=1)

    phot_apertures = models.FloatField(default=11.0)
    pixel_scale = models.FloatField(default=2.5)
    gain = models.FloatField(default=0.0)
    satur_level = models.FloatField(default=50000.0)

    def __str__(self):
        return 'sigma_psf: %f, crit_sep: %f, threshold: %f, box: %d, iters: %d' % \
                (self.sigma_psf, self.crit_separation, self.threshold, self.box_size, self.iters)

admin.site.register(ImageFilter)
admin.site.register(PhotometrySettings)
