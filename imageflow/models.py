from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

# Django's JSONField requires postgres, but this 3rd-party library provides a
# shim for databases without native json support.
from jsonfield import JSONField

from astrometry.models import AstrometrySubmissionJob
from lightcurve.models import LightCurve
from photometry.models import ImageFilter

class ImageAnalysis(models.Model):
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

    lightcurve = models.ForeignKey(LightCurve, null=True)

    astrometry_job = models.ForeignKey(AstrometrySubmissionJob)

    # Meta data.
    image_datetime = models.DateTimeField(null=True)
    image_filter = models.ForeignKey(ImageFilter, null=True)
    image_latitude = models.FloatField(default=0)
    image_longitude = models.FloatField(default=0)
    image_elevation = models.FloatField(default=0)

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
    image_reference_stars = JSONField()
    image_reference_stars_json_url = models.CharField(max_length=1024)
    catalog_reference_stars = JSONField()
    catalog_reference_stars_json_url = models.CharField(max_length=1024)

    def create_reduction_if_not_exists(self):
        if not hasattr(self, 'reduction'):
            self.reduction = Reduction(analysis=self)
            self.reduction.status = Reduction.CREATED
            self.reduction.color_index_1 = self.image_filter
            self.reduction.color_index_2 = self.image_filter
            self.reduction.save()

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
                'catalog_reference_stars': self.catalog_reference_stars,
            },
        }

    def __str__(self):
        return 'Sub %d Job %d, Band %s @ %s' % \
                (self.astrometry_job.submission.subid, \
                 self.astrometry_job.jobid, \
                 str(self.image_filter), \
                 str(self.image_datetime))


class Reduction(models.Model):
    CREATED = 'CREATED'
    PENDING = 'PENDING'
    RUNNING = 'RUNNING'
    COMPLETE = 'COMPLETE'
    FAILED = 'FAILED'
    STATUSES = (
        (CREATED, 'Created'),
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (COMPLETE, 'Complete'),
        (FAILED, 'Failed'),
    )
    status = models.CharField(
            max_length=50, choices=STATUSES, default=CREATED)
    analysis = models.OneToOneField(ImageAnalysis)

    # Data fields
    reduced_stars = JSONField()
    color_index_1 = models.ForeignKey(ImageFilter,
                                      related_name='reduction_color_index_1_set',
                                      default=ImageFilter.DEFAULT)
    color_index_2 = models.ForeignKey(ImageFilter,
                                      related_name='reduction_color_index_2_set',
                                      default=ImageFilter.DEFAULT_2)

    second_order_extinction = models.FloatField(default=0)
    tf = models.FloatField(null=True)
    tf_graph_url = models.CharField(max_length=1024, null=True)

    def get_summary_obj(self):
        return {
            'urls': {
                'tf_graph': self.tf_graph_url,
            },
            'meta': {
                'status': self.status,
            },
            'data': {
                'color_index_1_band': self.color_index_1.band if self.color_index_1 else '',
                'color_index_2_band': self.color_index_2.band if self.color_index_1 else '',
                'second_order_extinction': self.second_order_extinction,
                'reduced_stars': self.reduced_stars,
                'tf': self.tf,
            }
        }

    def __str__(self):
        return 'Reduction for Analysis %s' % (str(self.analysis))


class UserUploadedImage(models.Model):
    """
    Model for user uploaded images
    Author: Amr Draz
    """
    user = models.ForeignKey(User)
    image_url = models.URLField(max_length=512)
    astrometry_submission_id = models.CharField(max_length=512)
    created_at = models.DateTimeField(auto_now=True)

    lightcurve = models.ForeignKey(LightCurve, null=True)

    # Analysis result isn't filled until the job is actually processed.
    # analysis_result = models.ForeignKey(ImageAnalysis, null=True)

admin.site.register(ImageAnalysis)
admin.site.register(Reduction)
admin.site.register(UserUploadedImage)
