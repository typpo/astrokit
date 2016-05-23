import time

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

import imageflow.s3_util as s3_util
from astrometry.util import process_astrometry_online

def index(request):
    return render_to_response('index.html')

def upload_image(request):
    if request.method == 'POST':
        img = request.FILES['image']
        # Data is read just once to avoid rewinding.
        img_data = img.read()
        url = s3_util.upload_to_s3(img_data, 'raw', img.name)
        process_astrometry_online(url)

    return render_to_response('upload_image.html', {},
            context_instance=RequestContext(request))

def api_get_submission_results(request):
    return 'foo'
