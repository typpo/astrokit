from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

from astrometry.models import AstrometrySubmissionJob

class AnalysisResult(models.Model):
    PENDING = 'PENDING'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'
    STATUSES = (
        (PENDING, 'Pending'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    )
    status = models.CharField(
            max_length=50, choices=STATUSES, default=PENDING)

    user = models.ForeignKey(User)

    astrometry_job = models.ForeignKey(AstrometrySubmissionJob)

    # Processed output urls on S3.
    astrometry_annotated_display_url = models.CharField(max_length=1024)
    astrometry_image_fits_url = models.CharField(max_length=1024)
    astrometry_corr_fits_url = models.CharField(max_length=1024)

    coords_plot_url = models.CharField(max_length=1024)
    coords_fits_url = models.CharField(max_length=1024)
    coords_json_url = models.CharField(max_length=1024)

    # Point source extraction.
    psf_scatter_url = models.CharField(max_length=1024)
    psf_bar_url = models.CharField(max_length=1024)
    psf_hist_url = models.CharField(max_length=1024)
    psf_residual_image_url = models.CharField(max_length=1024)

    # Reference stars and magnitudes.
    reference_stars_json_url = models.CharField(max_length=1024)
    catalog_reference_stars_json_url = models.CharField(max_length=1024)

    def get_summary_obj(self):
        return {
            'jobid': self.astrometry_job.jobid,
            'urls': {
                'astrometry_annotated_display_url': self.astrometry_annotated_display_url,
                'astrometry_image_fits_url': self.astrometry_image_fits_url,
                'astrometry_corr_fits_url': self.astrometry_corr_fits_url,

                'coords_plot_url': self.coords_plot_url,
                'coords_fits_url': self.coords_fits_url,
                'coords_json_url': self.coords_json_url,

                'psf_scatter_url': self.psf_scatter_url,
                'psf_bar_url': self.psf_bar_url,
                'psf_hist_url': self.psf_hist_url,
                'psf_residual_image_url': self.psf_residual_image_url,
            },
        }


class UserUploadedImage(models.Model):
    """Model for user uploaded images
    Author: Amr Draz
    """
    user = models.ForeignKey(User)
    image_url = models.URLField(max_length=512)
    astrometry_submission_id = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now=True)


admin.site.register(AnalysisResult)
admin.site.register(UserUploadedImage)
