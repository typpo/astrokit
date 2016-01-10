from __future__ import unicode_literals

from django.db import models

class ImageModel(models.Model):
    image = models.ImageField(upload_to='uploaded_images/')
