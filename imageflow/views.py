import time

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

import boto
from boto.s3.key import Key

def upload_image(request):
    if request.method == 'POST':
        _upload_to_s3(request)

    return render_to_response('upload_image.html', {},
            context_instance=RequestContext(request))

def _upload_to_s3(request):
    img = request.FILES['image']

    conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
            settings.AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME,
            validate=True)
    k = Key(bucket)
    # TODO(ian): Some way to avoid collisions.
    k.key = 'raw/%d-%s' % (int(time.time()), img.name)
    # TODO(ian): Support other content types.
    k.set_metadata('Content-Type', 'image/jpeg')
    k.set_contents_from_file(img)
    k.set_acl('public-read')
