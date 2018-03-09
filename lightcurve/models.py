from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from photometry.models import ImageFilter

class LightCurve(models.Model):
    user = models.ForeignKey(User)

    name = models.CharField(max_length=1024)
    notes = models.TextField(default='')

    ciband = models.CharField(max_length=50, default='')

    magband = models.ForeignKey(ImageFilter,
                                related_name='lightcurve_magband_set',
                                default=ImageFilter.objects.get_default())

    def to_alcdef(self):
        return 'NYI'

    def get_ci_band1(self):
        return ImageFilter.objects.get_from_ci_band(self.ciband, 0)

    def get_ci_band2(self):
        return ImageFilter.objects.get_from_ci_band(self.ciband, 1)

admin.site.register(LightCurve)
