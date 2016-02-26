from __future__ import unicode_literals

import datetime

import django
from django.contrib import admin
from django.db import models
from jsonfield import JSONField

from astrometry_client import Client

class AstrometrySubmission(models.Model):
    SUBMITTED = 'SUBMITTED'
    COMPLETE = 'COMPLETE'
    FAILED_TO_SUBMIT = 'FAILED_TO_SUBMIT'
    SUBMISSION_STATUSES = (
        (SUBMITTED, 'Submitted'),
        (COMPLETE, 'Complete'),
        (FAILED_TO_SUBMIT, 'Failed to submit'),
    )
    subid = models.IntegerField()
    status = models.CharField(
            max_length=50, choices=SUBMISSION_STATUSES, default=SUBMITTED)
    created_at = models.DateTimeField(default=django.utils.timezone.now)
    succeeded_at = models.DateTimeField(blank=True, null=True)

    def get_astrometry_net_url(self):
        return 'http://nova.astrometry.net/user_images/%d' % self.subid

    def maybe_update_astrometry_net_status(self):
        client = Client()
        client.login(settings.ASTROKIT_ASTROMETRY_KEY)

        substatus = client.sub_status(self.subid)
        if substatus and substatus['status'] == 'processing_finished':
            self.status = COMPLETE

        # TODO(ian) Update related AstrometrySubmissionJobs.

admin.site.register(AstrometrySubmission)

class AstrometrySubmissionJob(models.Model):
    SUCCESS = 'SUCCESS'
    UNKNOWN = 'UNKNOWN'
    JOB_STATUSES = (
        (SUCCESS, 'Success'),
        (UNKNOWN, 'Unknown'),
    )

    submission = models.ForeignKey(
            AstrometrySubmission, on_delete=models.CASCADE)
    status = models.CharField(
            max_length=50, choices=JOB_STATUSES, default=UNKNOWN)
    succeeded_at = models.DateTimeField(blank=True, null=True)
    annotations = JSONField(blank=True, null=True)
