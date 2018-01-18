from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

class ImageFilterManager(models.Manager):
    def get_by_natural_key(self, band):
        return self.get(band=band)

class ImageFilter(models.Model):
    """
    Model for image filter
    """
    objects = ImageFilterManager()

    band = models.CharField(max_length=512)
    system = models.CharField(max_length=512)
    range_min_nm = models.IntegerField()
    urat1_key = models.CharField(max_length=50)

    def __str__(self):
        return '%s (%s)' % (self.band, self.system)

    def __unicode__(self):
        return u'%s (%s)' % (self.band, self.system)

admin.site.register(ImageFilter)
