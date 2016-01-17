from __future__ import unicode_literals

from django.contrib import admin
from django.db import models

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
    submission = models.ForeignKey(
            AstrometrySubmission, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
