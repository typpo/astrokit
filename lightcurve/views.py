from django.http import JsonResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from astrometry.models import AstrometrySubmission
from imageflow.models import ImageAnalysis, UserUploadedImage
from lightcurve.models import LightCurve

from astrometry.process import process_astrometry_online

def edit_lightcurve(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = UserUploadedImage.objects.filter(lightcurve=lc)
    context = {
        'lightcurve': lc,
        'images': images,
    }
    return render_to_response('lightcurve.html', context,
            context_instance=RequestContext(request))

def get_status(request, lightcurve_id):
    lc = LightCurve.objects.get(id=lightcurve_id)
    images = lc.useruploadedimage_set.all()
    num_processed = sum([image.submission.is_done() for image in images if image.submission])

    return JsonResponse({
        'success': True,
        'numProcessed': num_processed,
        'complete': num_processed == len(images),
    })
