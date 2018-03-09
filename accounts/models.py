from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

import random
import string


class URLCode(models.Model):
    """URLCode model generating user specific url codes
    used for forgot password links
    Author: Amr Draz
    """
    user = models.ForeignKey(User)
    code = models.CharField(max_length=16, unique=True)
    created_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        """ Generate a random code before saving
        Assert uniqueness of code
        Delete previous codes for this user
        Author: Amr Draz
        """
        previous_urlcodes = URLCode.objects.filter(user=self.user)
        if previous_urlcodes:
            previous_urlcodes.delete()

        self.code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
        while URLCode.objects.filter(code=self.code):
            self.code = ''.join(
                random.choice(
                    string.ascii_uppercase + string.ascii_lowercase + string.digits
                    ) for _ in range(16))

        super(URLCode, self).save(*args, **kwargs)

class UserUploadedImage(models.Model):
    """ Model for user uploaded images
    """
    user = models.ForeignKey(User)
    image_url = models.URLField(max_length=512)
    original_filename = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now=True)

    lightcurve = models.ForeignKey('lightcurve.LightCurve', blank=True, null=True)
    submission = models.ForeignKey('astrometry.AstrometrySubmission', blank=True, null=True)
    analysis = models.ForeignKey('imageflow.ImageAnalysis', blank=True, null=True)

    def __str__(self):
        return '%s submission #%d' % (self.original_filename, self.submission.subid)
