from __future__ import unicode_literals

from django.contrib import admin
from django.db import models

from astrometry.models import AstrometrySubmissionJob

class AnalysisResult(models.Model):
    astrometry_job = models.ForeignKey(AstrometrySubmissionJob)

    # Processed output urls on S3.
    astrometry_annotated_display_url = models.CharField(max_length=1024)
    astrometry_image_fits_url = models.CharField(max_length=1024)
    astrometry_corr_fits_url = models.CharField(max_length=1024)

    coords_plot_url = models.CharField(max_length=1024)
    coords_fits_url = models.CharField(max_length=1024)
    coords_json_url = models.CharField(max_length=1024)

    psf_scatter_url = models.CharField(max_length=1024)
    psf_bar_url = models.CharField(max_length=1024)
    psf_hist_url = models.CharField(max_length=1024)
    psf_residual_image_url = models.CharField(max_length=1024)

admin.site.register(AnalysisResult)
