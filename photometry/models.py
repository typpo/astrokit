from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

class ImageFilterManager(models.Manager):
    def get_default(self):
        return self.get(band='B').pk

    def get_default_2(self):
        return self.get(band='V').pk


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

class ColorIndex(models.Model):
    filter1 = models.ForeignKey(ImageFilter)
    filter2 = models.ForeignKey(ImageFilter)

    def __str__(self):
        return '%s - %s' % (self.filter1.band, self.filter2.band)

class PhotometrySettings(models.Model):
    sigma_psf = models.FloatField(default=2.0)
    crit_separation = models.FloatField(default=5.0)
    threshold = models.FloatField(default=5.0)
    box_size = models.IntegerField(default=11)
    iters = models.IntegerField(default=1)

admin.site.register(ImageFilter)
admin.site.register(PhotometrySettings)
