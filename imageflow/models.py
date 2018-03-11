from __future__ import unicode_literals

from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User

# Django's JSONField requires postgres, but this 3rd-party library provides a
# shim for databases without native json support.
from jsonfield import JSONField

from accounts.models import UserUploadedImage
from astrometry.models import AstrometrySubmission, AstrometrySubmissionJob
from lightcurve.models import LightCurve
from photometry.models import ImageFilter, PhotometrySettings

class ImageAnalysis(models.Model):
    ASTROMETRY_PENDING = 'ASTROMETRY_PENDING'
    PHOTOMETRY_PENDING = 'PHOTOMETRY_PENDING'
    REVIEW_PENDING = 'REVIEW_PENDING'
    REDUCTION_COMPLETE = 'REDUCTION_COMPLETE'
    ADDED_TO_LIGHT_CURVE = 'ADDED_TO_LIGHT_CURVE'
    FAILED = 'FAILED'
    STATUSES = (
        (ASTROMETRY_PENDING, 'Astrometry pending'),
        (PHOTOMETRY_PENDING, 'Photometry pending'),
        (REVIEW_PENDING, 'Review pending'),
        (REDUCTION_COMPLETE, "Reduction complete"),
        (ADDED_TO_LIGHT_CURVE, "Added to light curve"),
        (FAILED, 'Failed'),
    )
    status = models.CharField(
            max_length=50, choices=STATUSES, default=ASTROMETRY_PENDING)

    notes = models.TextField(default='')

    user = models.ForeignKey(User)

    lightcurve = models.ForeignKey(LightCurve, null=True)

    astrometry_job = models.ForeignKey(AstrometrySubmissionJob)

    # Meta data.
    image_datetime = models.DateTimeField(null=True)
    # Light-time corrected datetime, in JD.
    image_jd_corrected = models.FloatField(null=True)
    image_filter = models.ForeignKey(ImageFilter, default=ImageFilter.objects.get_default())
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

    # Point source extraction & photometry.
    photometry_settings = models.ForeignKey(PhotometrySettings, null=True)

    psf_scatter_url = models.CharField(max_length=1024)
    psf_bar_url = models.CharField(max_length=1024)
    psf_hist_url = models.CharField(max_length=1024)
    psf_residual_image_url = models.CharField(max_length=1024)

    sigma_clipped_std = models.FloatField(default=0)

    # ID of point source target.
    target_name = models.CharField(max_length=50)
    target_id = models.IntegerField(blank=True, null=True)
    target_x = models.IntegerField(default=-1)
    target_y = models.IntegerField(default=-1)

    # Reference stars and magnitudes:

    # Stars that are matched to an RA, DEC by astrometry service.
    image_reference_stars = JSONField()
    image_reference_stars_json_url = models.CharField(max_length=1024)

    # Of these stars with RA, DEC, these are the stars that were matched to
    # catalog.
    catalog_reference_stars = JSONField()
    catalog_reference_stars_json_url = models.CharField(max_length=1024)

    # Stars that weren't matched.
    image_unknown_stars = JSONField()
    image_unknown_stars_json_url = models.CharField(max_length=1024)

    # Everything put together.
    annotated_point_sources = JSONField()
    annotated_point_sources_json_url = models.CharField(max_length=1024)

    def get_uploaded_image_or_none(self):
        try:
            return UserUploadedImage.objects.get(analysis=self)
        except UserUploadedImage.DoesNotExist:
            return None

    def get_or_create_reduction(self):
        reduction, created = Reduction.objects.get_or_create(analysis=self)

        if created:
            reduction.analysis = self
            reduction.status = Reduction.CREATED
            reduction.save()
        return reduction

    def get_or_create_photometry_settings(self):
        if not self.photometry_settings:
            self.photometry_settings = PhotometrySettings.objects.create()
            self.save()
        return self.photometry_settings

    def get_summary_obj(self):
        return {
            'id': self.id,
            'jobid': self.astrometry_job.jobid,
            'subid': self.astrometry_job.submission.subid,
            'lightcurve_id': self.lightcurve.id,
            'meta': {
                'image_name_short': self.get_short_name(),
                'notes': self.notes,
                'datetime': self.image_datetime,
                'jd_corrected': self.image_jd_corrected,
                'latitude': self.image_latitude,
                'longitude': self.image_longitude,
                'elevation': self.image_elevation,
                'image_band': self.image_filter.band,
                'image_band_urat1_key': self.image_filter.urat1_key,
                'photometric_system': self.image_filter.system,
                # TODO(ian): Don't pass an object - can't be serialized to json.
                'uploaded_image': self.get_uploaded_image_or_none(),
                'target_id': self.target_id,
                'target_name': self.target_name,
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
                'comparison_star_ids': self.get_comparison_star_ids(),
                'unknown_stars': self.image_unknown_stars,

                'sigma_clipped_std': self.sigma_clipped_std,
            },
        }

    def get_short_name(self, maxlen=30):
        image = self.useruploadedimage_set.first()
        if image:
            name = image.original_filename
        else:
            name = 'Unknown image'

        if len(name) <= 30:
            return name

        # Half the size, minus the 3 dots.
        n_2 = maxlen / 2 - 3
        # Remainder
        n_1 = maxlen - n_2 - 3
        return '%s...%s' % (name[:n_1], name[-n_2:])

    def is_reviewed(self):
        '''Returns whether this image has been reviewed.
        '''
        return self.status in [ImageAnalysis.REDUCTION_COMPLETE, ImageAnalysis.ADDED_TO_LIGHT_CURVE]

    def is_photometry_complete(self):
        '''Returns whether this image is past the photometry stage.
        '''
        return self.is_reviewed() or self.status == 'REVIEW_PENDING'

    def get_comparison_star_ids(self):
        desigs = set([star['designation'] for star in self.lightcurve.comparison_stars])
        return [star['id'] for star in self.annotated_point_sources if star.get('designation') in desigs]

    def __str__(self):
        return '#%d %s: %s - Sub %d Job %d, Band %s @ %s' % \
                (self.id,
                 self.get_short_name(),
                 self.status,
                 self.astrometry_job.submission.subid, \
                 self.astrometry_job.jobid, \
                 str(self.image_filter.band), \
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
    analysis = models.OneToOneField(ImageAnalysis, related_name='reduction')

    # TODO(ian): rename to reduced_points, because it can contain unknown objects.
    reduced_stars = JSONField()

    image_companion = models.ForeignKey(UserUploadedImage, null=True, blank=True)

    def get_summary_obj(self):
        return {
            'urls': {
            },
            'meta': {
                'status': self.status,
                'image_companion_id': self.image_companion.id if self.image_companion else None,
            },
            'data': {
                'reduced_stars': self.reduced_stars,
            }
        }

    def __str__(self):
        return 'Reduction for Analysis %s' % (str(self.analysis))

class ImageAnalysisPair(models.Model):
    lightcurve = models.ForeignKey(LightCurve)

    analysis1 = models.ForeignKey(ImageAnalysis, related_name='analysis1_set')
    analysis2 = models.ForeignKey(ImageAnalysis, related_name='analysis2_set')

admin.site.register(ImageAnalysis)
admin.site.register(ImageAnalysisPair)
admin.site.register(Reduction)
