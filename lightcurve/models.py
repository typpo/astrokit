from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from photometry.models import ImageFilter

class LightCurve(models.Model):
    user = models.ForeignKey(User, null=True)

    name = models.CharField(max_length=1024)

    image_filter = models.ForeignKey(ImageFilter, related_name='lightcurve_image_filter_set')
    magband = models.ForeignKey(ImageFilter, related_name='lightcurve_magband_set')

    def to_alcdef(self):
        return 'NYI'

admin.site.register(LightCurve)
