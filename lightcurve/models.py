from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.models import User
from django.db import models

from jsonfield import JSONField

from photometry.models import ImageFilter

class LightCurve(models.Model):
    CREATED = 'CREATED'
    PHOTOMETRY_PENDING = 'PHOTOMETRY_PENDING'
    REDUCTION_PENDING = 'REDUCTION_PENDING'
    REDUCTION_COMPLETE = 'REDUCTION_COMPLETE'
    STATUSES = (
        (CREATED, 'Created'),
        (PHOTOMETRY_PENDING, 'Photometry pending'),
        (REDUCTION_PENDING, 'Reduction pending'),
        (REDUCTION_COMPLETE, 'Reduction complete'),
    )
    status = models.CharField(
            max_length=50, choices=STATUSES, default=CREATED)

    user = models.ForeignKey(User)

    name = models.CharField(max_length=1024)
    notes = models.TextField(default='')

    ciband = models.CharField(max_length=50, default='')

    filter = models.ForeignKey(ImageFilter,
                               related_name='lightcurve_filter_set',
                               default=ImageFilter.objects.get_default())

    magband = models.ForeignKey(ImageFilter,
                                related_name='lightcurve_magband_set',
                                default=ImageFilter.objects.get_default())

    common_stars = JSONField()
    comparison_stars = JSONField()

    def to_alcdef(self):
        return 'NYI'

    def get_ci_band1(self):
        bandstr = ImageFilter.objects.get_from_ci_band(self.ciband, 0)
        return ImageFilter.objects.get(band=bandstr)

    def get_ci_band2(self):
        bandstr = ImageFilter.objects.get_from_ci_band(self.ciband, 1)
        return ImageFilter.objects.get(band=bandstr)

    def get_or_create_reduction(self):
        reduction, created = LightCurveReduction.objects.get_or_create(lightcurve=self)
        if created:
            reduction.lightcurve = self
            reduction.save()
        return reduction

    def get_common_desigs(self):
        return [star['designation'] for star in common_stars]

    def get_comparison_desigs(self):
        return [star['designation'] for star in comparison_stars]

    def is_photometry_complete(self):
        return self.status in [LightCurve.REDUCTION_PENDING, LightCurve.REDUCTION_COMPLETE]

class LightCurveReduction(models.Model):
    lightcurve = models.OneToOneField(LightCurve)

    # Extinction.
    second_order_extinction = models.FloatField(default=0)

    # Transformation coefficient calculation.
    tf = models.FloatField(null=True)
    tf_std = models.FloatField(null=True)
    tf_graph_url = models.CharField(max_length=1024, null=True)
    zpf = models.FloatField(null=True)

    # Hidden transform calculation.
    hidden_transform = models.FloatField(null=True)
    hidden_transform_intercept = models.FloatField(null=True)
    hidden_transform_std = models.FloatField(null=True)
    hidden_transform_rval = models.FloatField(null=True)
    hidden_transform_graph_url = models.CharField(max_length=1024, null=True)

    # Color index of targets
    color_index_manual = models.FloatField(null=True)
    color_index = models.FloatField(null=True)

admin.site.register(LightCurve)
admin.site.register(LightCurveReduction)
