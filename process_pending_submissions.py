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
    print 'Querying for submission %d...' % (submission.subid)
    substatus = client.sub_status(submission.subid, True)

    if substatus and 'processing_finished' in substatus:
        print '-> Submission is finished'

        job_ids = substatus['jobs']
        print 'Processing jobs: %s' % (job_ids)
        num_success = 0
        for job_id in job_ids:
            info = client.send_request('jobs/%d/info' % (job_id))
            if info['status'] == 'solving':
                print '-> Job %d is still solving' % (job_id)
                continue
            elif info['status'] != 'success':
                print '-> Warning: unsuccessful job %d for submission %d' \
                        % (job_id, submission.subid)
                continue

            annotations = json.dumps(client.send_request('jobs/%d/annotations' \
                    % (job_id)))

            # Save these results.
            job = AstrometrySubmissionJob.objects.create(
                    submission=submission,
                    status=AstrometrySubmissionJob.SUCCESS,
                    annotations=annotations)
            num_success += 1

        if num_success == len(job_ids):
            # Update submission.
            submission.succeeded_at = datetime.datetime.now()
            submission.status = AstrometrySubmission.COMPLETE
            submission.save()
