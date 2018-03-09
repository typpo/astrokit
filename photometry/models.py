from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

CI_BAND_TO_FILTERS = {
    'BV': ('B', 'V'),
    'VR': ('V', 'R'),
    'VI': ('V', 'I'),
    'SGU': ('g', 'u'),
    'SGR': ('g', 'r'),
    'SRI': ('r', 'i'),
    'SIZ': ('i', 'z'),
}

class ImageFilterManager(models.Manager):
    def get_default(self):
        return self.get(band='B').pk

    def get_default_2(self):
        return self.get(band='V').pk

    def get_from_ci_band(self, ci_band, pos):
        filters = CI_BAND_TO_FILTERS.get(ci_band)
        if not filters or pos not in [0, 1]:
            return None
        return filters[pos]

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
    sigma_psf = models.FloatField(default=2.0)
    crit_separation = models.FloatField(default=5.0)
    threshold = models.FloatField(default=5.0)
    box_size = models.IntegerField(default=11)
    iters = models.IntegerField(default=1)

admin.site.register(ImageFilter)
admin.site.register(PhotometrySettings)
