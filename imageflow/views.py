import time

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

import boto
from boto.s3.key import Key

from astrometry.util import process_astrometry_online

def upload_image(request):
    if request.method == 'POST':
        img = request.FILES['image']
        # Data is read just once to avoid rewinding.
        img_data = img.read()
        url = _upload_to_s3(img.name, img_data)
        process_astrometry_online(url)

    return render_to_response('upload_image.html', {},
            context_instance=RequestContext(request))

def _upload_to_s3(name, img_data):
    '''
    Upload an image to s3 and return the url to it.
    '''
    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME,
            validate=True)
    k = Key(bucket)
    # TODO(ian): Some way to avoid collisions.
    k.key = 'raw/%d-%s' % (int(time.time()), name)
    # TODO(ian): Support other content types.
    k.set_metadata('Content-Type', 'image/jpeg')
    k.set_contents_from_string(img_data)
    k.set_acl('public-read')
    return k.generate_url(expires_in=0, query_auth=False)
