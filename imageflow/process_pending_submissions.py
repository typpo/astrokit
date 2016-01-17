from django.conf import settings

from models import AstrometrySubmission
from astrometry_client import Client

client = Client()
client.login(settings.ASTROKIT_ASTROMETRY_KEY)

# TODO replace with some polling mechanism.
substatus = client.sub_status(subid)
if substatus and 'processing_finished' in substatus:
    for jobid in substatus['jobs']:
        jobstatus = c.job_status(jobid)
        # Read the results...
