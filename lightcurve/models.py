from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist


from photometry.models import ImageFilter

class LightCurve(models.Model):
    user = models.ForeignKey(User)

    name = models.CharField(max_length=1024)

    notes = models.TextField(default='')

    magband = models.ForeignKey(ImageFilter,
                                related_name='lightcurve_magband_set',
                                default=ImageFilter.objects.get_default())

    def save(self, user, *args, **kwargs):
        if user:
          if user == self.user:
                super(LightCurve, self).save(*args, **kwargs)
          else:
              raise PermissionDenied('User not the creater of this object.')
        else:
          raise ObjectDoesNotExist('Save() was called without passing in user')

    def to_alcdef(self):
        return 'NYI'

admin.site.register(LightCurve)
