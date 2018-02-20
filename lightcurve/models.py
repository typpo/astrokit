from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import PermissionDenied


from photometry.models import ImageFilter

class LightCurve(models.Model):
    user = models.ForeignKey(User)

    name = models.CharField(max_length=1024)

    notes = models.TextField(default='')

    magband = models.ForeignKey(ImageFilter,
                                related_name='lightcurve_magband_set',
                                default=ImageFilter.objects.get_default())

    def save(self, *args, **kwargs):
        orig = LightCurve.objects.get(id=self.id)
        if self.user == orig.user:
            super(LightCurve, self).save(*args, **kwargs)
        else:
            raise PermissionDenied('User not the creater of this object.')

    def to_alcdef(self):
        return 'NYI'

admin.site.register(LightCurve)
