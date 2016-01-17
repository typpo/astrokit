import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
sys.path.insert(0, os.getcwd())
django.setup()

from django.conf import settings

from astrometry.models import AstrometrySubmission
from astrometry.astrometry_client import Client

client = Client()
client.login(settings.ASTROKIT_ASTROMETRY_KEY)

pending_submissions = AstrometrySubmission.objects.all().filter(
        status=AstrometrySubmission.SUBMITTED)
for submission in pending_submissions:
    # TODO replace with some polling mechanism.
    substatus = client.sub_status(submission.subid, True)
    if substatus and 'processing_finished' in substatus:
        print client.submission_images(submission.subid)
        for jobid in substatus['jobs']:
            objs_in_field = client.send_request('jobs/%d/objects_in_field' \
                    % (jobid))
            print objs_in_field
            calibration = client.send_request('jobs/%d/calibration' \
                    % (jobid))
            print calibration
            machine_tags = client.send_request('jobs/%d/machine_tags' \
                    % (jobid))
            print machine_tags
            annotations = client.send_request('jobs/%d/annotations' \
                    % (jobid))
            print annotations

            # Read the results...
