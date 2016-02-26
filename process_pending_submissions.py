#!/usr/bin/env python

import datetime
import json
import os
import sys

import django
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

from astrometry.models import AstrometrySubmission
from astrometry.astrometry_client import Client

client = Client()
client.login(settings.ASTROKIT_ASTROMETRY_KEY)

pending_submissions = AstrometrySubmission.objects.all().filter(
        status=AstrometrySubmission.SUBMITTED)
for submission in pending_submissions:
    # TODO(ian) Run this automatically.
    substatus = client.sub_status(submission.subid, True)
    if substatus and 'processing_finished' in substatus:
        print client.submission_images(submission.subid)
        for jobid in substatus['jobs']:
            info = json.dumps(client.send_request('jobs/%d/info' % (jobid)))
            if info['status'] != 'success':
                print 'Warning: unsuccessful job %d for submission %d' \
                        % (jobid, submission.subid)
                continue
            annotations = json.dumps(client.send_request('jobs/%d/annotations' \
                    % (jobid)))

            # Save these results.
            job = AstrometrySubmissionJob.objects.create(
                    submission=submission,
                    status=AstrometrySubmissionJob.SUCCESS,
                    annotations=annotations)

        # Update submission.
        submission.succeeded_at = datetime.datetime.now()
        submission.status = AstrometrySubmission.COMPLETE
        submission.save()
