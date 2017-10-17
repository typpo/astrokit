from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

# Django's JSONField requires postgres, but this 3rd-party library provides a
# shim for databases without native json support.
from jsonfield import JSONField

from astrometry.models import AstrometrySubmissionJob

class ImageFilter(models.Model):
    """
    Model for image filter
    """
    band = models.CharField(max_length=512)
    system = models.CharField(max_length=512)
    range_min_nm = models.IntegerField()

    def __str__(self):
        return '%s (%s)' % (self.band, self.system)

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

    # Meta data.
    image_datetime = models.DateTimeField(null=True)
    image_filter = models.ForeignKey(ImageFilter, null=True)
    image_latitude = models.FloatField()
    image_longitude = models.FloatField()
    image_elevation_m = models.FloatField()


    # Processed output urls on S3.
    astrometry_original_display_url = models.CharField(max_length=1024)
    astrometry_annotated_display_url = models.CharField(max_length=1024)
    astrometry_image_fits_url = models.CharField(max_length=1024)
    astrometry_corr_fits_url = models.CharField(max_length=1024)

    coords_plot_url = models.CharField(max_length=1024)
    coords_fits_url = models.CharField(max_length=1024)
    original_display_url = models.CharField(max_length=1024)

    coords = JSONField()
    coords_json_url = models.CharField(max_length=1024)

    # Point source extraction.
    psf_scatter_url = models.CharField(max_length=1024)
    psf_bar_url = models.CharField(max_length=1024)
    psf_hist_url = models.CharField(max_length=1024)
    psf_residual_image_url = models.CharField(max_length=1024)

    # Reference stars and magnitudes.
    reference_stars = JSONField()
    reference_stars_json_url = models.CharField(max_length=1024)
    catalog_reference_stars = JSONField()
    catalog_reference_stars_json_url = models.CharField(max_length=1024)

    def get_summary_obj(self):
        return {
            'jobid': self.astrometry_job.jobid,
            'subid': self.astrometry_job.submission.subid,
            'meta': {
                'datetime': self.image_datetime,
                'latitude': self.image_latitude,
                'longitude': self.image_longitude,
                'elevation': self.image_elevation,
                'image_band': self.image_filter.band if self.image_filter else '',
                'photometric_system': self.image_filter.system if self.image_filter else '',
            },
            'urls': {
                'astrometry_original_display_url': self.astrometry_original_display_url,
                'astrometry_annotated_display_url': self.astrometry_annotated_display_url,
                'astrometry_image_fits_url': self.astrometry_image_fits_url,
                'astrometry_corr_fits_url': self.astrometry_corr_fits_url,

                'original_display_url': self.original_display_url,
                'coords_plot_url': self.coords_plot_url,
                'coords_fits_url': self.coords_fits_url,
                'coords_json_url': self.coords_json_url,

                'psf_scatter_url': self.psf_scatter_url,
                'psf_bar_url': self.psf_bar_url,
                'psf_hist_url': self.psf_hist_url,
                'psf_residual_image_url': self.psf_residual_image_url,
            },
            'data': {
                'coords': self.coords,
                'reference_stars': self.reference_stars,
                'catalog_reference_stars': self.catalog_reference_stars,
            },
        }

    def __str__(self):
        return 'Sub %d Job %d, Band %s @ %s' % \
                (self.astrometry_job.submission.subid, \
                 self.astrometry_job.jobid, \
                 str(self.image_filter), \
                 str(self.image_datetime))


class UserUploadedImage(models.Model):
    """
    Model for user uploaded images
    Author: Amr Draz
    """
    user = models.ForeignKey(User)
    image_url = models.URLField(max_length=512)
    astrometry_submission_id = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now=True)

    # Analysis result isn't filled until the job is actually processed.
    # analysis_result = models.ForeignKey(AnalysisResult, null=True)

admin.site.register(AnalysisResult)
admin.site.register(UserUploadedImage)
admin.site.register(ImageFilter)
